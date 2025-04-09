from rest_framework import serializers
from .models import Request
from django.contrib.auth.models import User

class RequestSerializer(serializers.ModelSerializer):
    signature = serializers.ImageField(required=False, allow_null = True)
    admin_signature = serializers.ImageField(required=False, allow_null = True)

    class Meta:
        model = Request
        fields = ['id', 'status', 'reason_for_return', 'data', 'form_type', 'pdf', 'signature', 'admin_signature']
        read_only_fields = ['id'] 