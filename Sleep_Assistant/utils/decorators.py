from functools import wraps
from django.http import JsonResponse

def session_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            return JsonResponse({'status': 'error', 'message': '用户未登录'}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view