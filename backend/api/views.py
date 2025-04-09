import os
import base64
import requests
from .models import Request
from .serializers import RequestSerializer
from django.shortcuts import get_object_or_404
from django_tex.shortcuts import render_to_pdf
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import FileResponse
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from allauth.socialaccount.providers.microsoft.views import MicrosoftGraphOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

class MicrosoftLogin(SocialLoginView):
    adapter_class = MicrosoftGraphOAuth2Adapter
    callback_url = 'http://localhost:5173'
    client_class = OAuth2Client

class MicrosoftAuthURL(APIView):
    def get(self, request):
        redirect_uri = 'http://localhost:5173/microsoft-callback'
        scope = ['openid', 'profile', 'email', 'User.Read']  
        client_id = settings.SOCIAL_AUTH_MICROSOFT_OAUTH2_KEY
        
        url = f"https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={' '.join(scope)}"
        
        return Response({'auth_url': url})

class MicrosoftCallbackView(APIView):
    def post(self, request):
        code = request.data.get('code')
        
        if not code:
            return Response({'error': 'Authorization code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client_id = settings.SOCIAL_AUTH_MICROSOFT_OAUTH2_KEY
            client_secret = settings.SOCIAL_AUTH_MICROSOFT_OAUTH2_SECRET
            redirect_uri = 'http://localhost:5173/microsoft-callback'
            
            token_url = 'https://login.microsoftonline.com/organizations/oauth2/v2.0/token'
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
            
            response = requests.post(token_url, data=token_data)
            token_response = response.json()
            
            if 'error' in token_response:
                return Response({'error': token_response.get('error_description', 'Unknown error')}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            access_token = token_response['access_token']
            user_info_url = 'https://graph.microsoft.com/v1.0/me'
            headers = {'Authorization': f'Bearer {access_token}'}
            
            user_response = requests.get(user_info_url, headers=headers)
            user_data = user_response.json()
            email = user_data.get('mail') or user_data.get('userPrincipalName')
            if not email:
                return Response({'error': 'Could not retrieve email from Microsoft account'}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(email__iexact=email)
                if not user.first_name and user_data.get('givenName'):
                    user.first_name = user_data.get('givenName', '')
                if not user.last_name and user_data.get('surname'):
                    user.last_name = user_data.get('surname', '')
                user.save(update_fields=['first_name', 'last_name'])
            except User.DoesNotExist:
                username = email.split('@')[0]
                base_username = username
                counter = 1
                
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=user_data.get('givenName', ''),
                    last_name=user_data.get('surname', '')
                )
            
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'isSuperUser': user.is_superuser,
                'userName': user.username,
                'firstName': user.first_name,
                'lastName': user.last_name
            })
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Microsoft login error: {str(e)}", exc_info=True)
            return Response({'error': f"Authentication failed: {str(e)}"}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return Response({'message': 'Account created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            response_data = ({
                "token": token.key,
                "isSuperUser": user.is_superuser,
                "userName": user.username,
                'firstName': user.first_name,
                'lastName': user.last_name
            })
            return Response(response_data)
            
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        
class UserFormsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        user_requests = Request.objects.filter(user=user)

        serializer = RequestSerializer(user_requests, many=True)

        return Response(serializer.data)


class RequestSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.data:
            return Response({"error": "No data provided."}, status=status.HTTP_400_BAD_REQUEST)

        form_data = request.data
        form_type = form_data.get("form_type")
        user = request.user
        status_value = form_data.get("status", "draft")
        signature_data = form_data.get('signature')
        signature_file = None
        if signature_data:
            signature_file = self._convert_base64_to_image(signature_data)
        try:
            request_instance = Request.objects.create(
                user=user,
                status=status_value,
                form_type=form_type,
                data=form_data,
                signature=signature_file
            )
            
            return self._process_request(request, request_instance, status_value)
            
        except Exception as e:
            return Response({"error": f"Failed to save the request: {str(e)}"}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk=None):
        if not request.data:
            return Response({"error": "No data provided."}, status=status.HTTP_400_BAD_REQUEST)

        form_data = request.data
        user = request.user
        status_value = form_data.get("status", "draft")
        signature_data = form_data.get('signature')
        signature_file = None
        if signature_data:
            signature_file = self._convert_base64_to_image(signature_data)

        try:
            request_instance = get_object_or_404(Request, id=pk, user=user)
            request_instance.data = form_data
            request_instance.status = status_value


            if signature_file:
                request_instance.signature = signature_file

            request_instance.save()

            return self._process_request(request, request_instance, status_value)
            
        except Exception as e:
            return Response({"error": f"Failed to update the request: {str(e)}"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def _convert_base64_to_image(self, base64_data):
        try:
            format, imgstr = base64_data.split(';base64,')
            ext = 'jpg' 
            img_data = base64.b64decode(imgstr)


            image_name = f"signature.{ext}"
            image_file = ContentFile(img_data, name=image_name)
            return image_file
        except Exception as e:
            raise ValidationError(f"Invalid signature data: {str(e)}")
        
    
    def _process_request(self, request, request_instance, status_value):
        if status_value == 'submitted' and not request_instance.pdf:
            template_name = "pdf_templates/diploma_template.tex"
            if request_instance.form_type == "ChangeAddressForm":
                template_name = "pdf_templates/change_address_template.tex"
            context = request_instance.data
            
            try:
                pdf_path = self.generate_pdf(request, template_name, context, request_instance)
                if not pdf_path:
                    return Response({"error": "Failed to generate PDF"}, 
                                   status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": f"PDF generation failed: {str(e)}"}, 
                               status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = RequestSerializer(request_instance)
        return Response({
            "message": "Request saved successfully.",
            "request": serializer.data
        })

    def generate_pdf(self, request, template_name, context, request_instance):
        def flatten_dict(d):
            flat = {}
            for key, value in d.items():
                if isinstance(value, dict):
                    flat.update(flatten_dict(value))
                else:
                    flat[key] = value
            return flat

        context = flatten_dict(context)

        context['graphicspath'] = os.path.join(settings.MEDIA_ROOT, 'signatures').replace("\\", "/")


        if request_instance.signature:
            context['signature'] = request_instance.signature.path.replace("\\", "/")
        else:
            context['signature'] = None
            
        form_type = request_instance.form_type
        pdf_file_name = f'{form_type}_{request_instance.id}.pdf'

        pdf_path = os.path.join(f'{form_type}_pdfs', pdf_file_name)
        full_path = os.path.join(settings.MEDIA_ROOT, pdf_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        try:
            rendered_pdf = render_to_pdf(request, template_name, context)
            
            if rendered_pdf is None:
                raise ValueError("PDF rendering returned None")
            
            with open(full_path, 'wb') as f:
                f.write(rendered_pdf.content)

            request_instance.pdf.name = pdf_path
            request_instance.save()

            return full_path
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating PDF: {e}", exc_info=True)
            return None
    
def servePDF(request, request_id):
    req = get_object_or_404(Request, id=request_id)

    if req.pdf:
        return FileResponse(req.pdf, content_type='application/pdf')
    else:
        return HttpResponse('PDF not found', status=404)
    
class RequestDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        user_request = get_object_or_404(Request, id=pk, user=request.user)
        
        user_request.delete()

        return Response({"message": "Form deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class AdminRequestsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        submitted_requests = Request.objects.exclude(status='draft')
        serializer = RequestSerializer(submitted_requests, many=True)
        return Response(serializer.data)
    
class RequestApprovalView(APIView):
    permission_classes = [IsAdminUser]
    
    def put(self, request, pk):
        req = get_object_or_404(Request, id=pk)


        new_status = request.data.get("status")
        if new_status not in ['approved', 'rejected']:
            return Response(
                {"error": "Invalid status. Must be 'approved' or 'rejected'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if new_status == "rejected":
            reason = request.data.get("reason_for_return", "")
            req.reason_for_return = reason
        else:
            req.reason_for_return = None


        admin_signature_data = request.data.get('admin_signature')
        admin_signature_file = None

        if admin_signature_data:
            admin_signature_file = self._convert_base64_to_image(admin_signature_data)

        if admin_signature_file:
            try:
                req.admin_signature = admin_signature_file
                req.status = new_status 
                req.save()

                return self._process_request(request, req, new_status)
            except Exception as e:
                return Response({"error": f"Failed to save the admin signature: {str(e)}"}, 
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        req.status = new_status
        req.save()

        return Response(
            {"message": f"Request {new_status} successfully."},
            status=status.HTTP_200_OK,
        )
    # * -------------- Everything below this needs to be refactored somehow -------------- *
    # Redundant code used in RequestSubmitView
    def _convert_base64_to_image(self, base64_data):
        try:
            format, imgstr = base64_data.split(';base64,')
            ext = 'jpg' 
            img_data = base64.b64decode(imgstr)

            image_name = f"admin_signature.{ext}"
            image_file = ContentFile(img_data, name=image_name)
            return image_file
        except Exception as e:
            raise ValidationError(f"Invalid signature data: {str(e)}")

    def _process_request(self, request, request_instance, status_value):
        if status_value == 'approved':
            template_name = "pdf_templates/diploma_template_admin.tex"
            if request_instance.form_type == "ChangeAddressForm":
                template_name = "pdf_templates/change_address_template_admin.tex"
            context = request_instance.data

            try:
                pdf_path = self.generate_pdf(request, template_name, context, request_instance)
                if not pdf_path:
                    return Response({"error": "Failed to generate PDF"}, 
                                     status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": f"PDF generation failed: {str(e)}"}, 
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = RequestSerializer(request_instance)
        return Response({
            "message": "Request saved successfully.",
            "request": serializer.data
        })

    def generate_pdf(self, request, template_name, context, request_instance):
        def flatten_dict(d):
            flat = {}
            for key, value in d.items():
                if isinstance(value, dict):
                    flat.update(flatten_dict(value))
                else:
                    flat[key] = value
            return flat

        context = flatten_dict(context)

        context['graphicspath'] = os.path.join(settings.MEDIA_ROOT, 'signatures').replace("\\", "/")
        context['signature'] = request_instance.signature.path.replace("\\", "/") if request_instance.signature else None
        context['admin_signature'] = request_instance.admin_signature.path.replace("\\", "/") if request_instance.admin_signature else None

        form_type = request_instance.form_type
        pdf_file_name = f'{form_type}_{request_instance.id}.pdf'

        pdf_path = os.path.join(f'{form_type}_pdfs', pdf_file_name)
        full_path = os.path.join(settings.MEDIA_ROOT, pdf_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        try:
            rendered_pdf = render_to_pdf(request, template_name, context)

            if rendered_pdf is None:
                raise ValueError("PDF rendering returned None")

            with open(full_path, 'wb') as f:
                f.write(rendered_pdf.content)

            request_instance.pdf.name = pdf_path
            request_instance.save()

            return full_path

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating PDF: {e}", exc_info=True)
            return None

