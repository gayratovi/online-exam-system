from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def role_required(role_name):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if getattr(request.user, 'role', None) != role_name:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator

staff_required = role_required('staff')
student_required = role_required('student')
