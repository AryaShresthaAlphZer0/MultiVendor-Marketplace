from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, VendorProfile


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Show our extra fields in the edit form
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Marketplace", {"fields": ("role", "phone")}),
    )
    # Show them when creating a user in the admin too
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Marketplace", {"fields": ("email", "role", "phone")}),
    )
    list_display = ("username", "email", "role", "is_staff", "created_at")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ("shop_name", "user", "is_verified", "created_at")
    list_filter = ("is_verified",)
    search_fields = ("shop_name", "user__username", "user__email")