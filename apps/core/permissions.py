from rest_framework.permissions import SAFE_METHODS, BasePermission


def _has_role(user, role):
    """True if the user is logged in and has the given role."""
    return bool(user and user.is_authenticated and user.role == role)


class IsVendor(BasePermission):
    """Only logged-in users with the vendor role."""

    message = "Only vendors can perform this action."

    def has_permission(self, request, view):
        return _has_role(request.user, "vendor")


class IsCustomer(BasePermission):
    """Only logged-in users with the customer role."""

    message = "Only customers can perform this action."

    def has_permission(self, request, view):
        return _has_role(request.user, "customer")


class IsVendorOrReadOnly(BasePermission):
    """Anyone can read; only vendors can write."""

    message = "Only vendors can modify this resource."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return _has_role(request.user, "vendor")


class IsOwner(BasePermission):
    """
    Object-level: only the owner of the object can access it.

    The owner field name is read from the view's `owner_field` attribute
    (default: "user"). Examples:
        ProductViewSet.owner_field = "vendor"
        OrderViewSet.owner_field = "customer"
    """

    message = "You do not have permission to access this object."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        owner_field = getattr(view, "owner_field", "user")
        return getattr(obj, owner_field, None) == request.user


class IsOwnerOrReadOnly(IsOwner):
    """Object-level: anyone can read; only the owner can change or delete."""

    def has_permission(self, request, view):
        # Reading is public; writing requires login.
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return super().has_object_permission(request, view, obj)