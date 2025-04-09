from django.db import models
from django.db.models import JSONField 
from django.contrib.auth.models import User

# Create your models here.
class Request(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('returned', 'Returned'),
        ('approved', 'Approved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    #user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    reason_for_return = models.TextField(blank=True, null=True)
    data = JSONField(blank=True, null=True)
    form_type = models.CharField(max_length=100) 
    pdf = models.FileField(upload_to='diploma_pdfs/', null=True, blank=True)
    signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    admin_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    def __str__(self):
        return f"{self.form_type} request by {self.user.username} (Status: {self.status})"