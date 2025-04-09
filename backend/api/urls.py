from django.urls import include, path
from .views import RequestSubmitView, SignupView, LoginView, UserFormsView, servePDF, RequestDeleteView, AdminRequestsView, RequestApprovalView, MicrosoftLogin, MicrosoftAuthURL, MicrosoftCallbackView

urlpatterns = [
    # Users can view these
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/forms/', UserFormsView.as_view(), name='user-forms'),
    path('admin/requests/', AdminRequestsView.as_view(), name='admin-requests'),
    path('microsoft-login/', MicrosoftLogin.as_view(), name='microsoft-login'),
    path('auth/', include('allauth.urls')),

    # For managing forms
    path('forms/', RequestSubmitView.as_view(), name='form'),
    path('forms/<int:pk>/', RequestSubmitView.as_view(), name='form'),
    path('forms/<int:request_id>/pdf/', servePDF, name='serve_pdf'),
    path('forms/<int:pk>/delete/', RequestDeleteView.as_view(), name='delete_form'),
    path('admin/requests/<int:pk>/approved/', RequestApprovalView.as_view(), name='admin-approve-request'),
    path('admin/requests/<int:pk>/rejected/', RequestApprovalView.as_view(), name='admin-reject-request'),

    path('microsoft/', MicrosoftLogin.as_view(), name='microsoft_login'),
    path('microsoft/auth-url/', MicrosoftAuthURL.as_view(), name='microsoft_auth_url'),
    path('microsoft/callback/', MicrosoftCallbackView.as_view(), name='microsoft_callback'),
]