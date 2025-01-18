from functools import wraps
from django.http import JsonResponse

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            # Access request object correctly when used with class-based views
            payload = getattr(request, "jwt_payload", None)
            if not payload:
                return JsonResponse({"error": "Unauthorized"}, status=401)
            if payload.get("role") != required_role:
                return JsonResponse({"error": "Forbidden: insufficient role"}, status=403)
            return view_func(self, request, *args, **kwargs)  # Pass all arguments correctly
        return _wrapped_view
    return decorator
