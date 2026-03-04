from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from functools import wraps

def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role != "admin":
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper