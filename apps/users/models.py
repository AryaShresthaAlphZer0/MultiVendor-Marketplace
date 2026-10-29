from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampModel


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        VENDOR = "vendor", "Vendor"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
 
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property # to access like a attribute
    def is_vendor(self):
        return self.role == self.Role.VENDOR

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER


class VendorProfile(TimeStampModel):
   

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_profile",
        limit_choices_to={"role": "vendor"},# from user
    )
    shop_name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="vendors/logos/", blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.shop_name