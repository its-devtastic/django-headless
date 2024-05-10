from rest_framework.permissions import DjangoModelPermissions, BasePermission


class DefaultPermission(DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class AllowRead(BasePermission):
    def has_permission(self, request, view):
        if hasattr(view, "action"):
            return view.action in ["list", "retrieve"]
        return False


class AllowRetrieve(BasePermission):
    def has_permission(self, request, view):
        if hasattr(view, "action"):
            return view.action == "retrieve"
        return False


class AllowList(BasePermission):
    def has_permission(self, request, view):
        if hasattr(view, "action"):
            return view.action == "list"
        return False


class AllowCreate(BasePermission):
    def has_permission(self, request, view):
        if hasattr(view, "action"):
            return view.action == "create"
        return False


class AllowUpdate(BasePermission):
    def has_permission(self, request, view):
        if hasattr(view, "action"):
            return view.action in ["update", "partial_update"]
        return False


class AllowDelete(BasePermission):
    def has_permission(self, request, view):
        if hasattr(view, "action"):
            return view.action == "destroy"
        return False
