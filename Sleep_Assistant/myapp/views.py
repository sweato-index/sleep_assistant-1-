from django.shortcuts import render
from django.http import JsonResponse
from .models import User

def get_all_user_ids(request):
    user_ids = list(User.objects.values_list('user_id', flat=True))
    user_names = list(User.objects.values_list('user_name', flat=True))
    user_emails = list(User.objects.values_list('email', flat=True))
    return JsonResponse({'user_ids': user_ids, 'user_names': user_names, 'user_emails': user_emails})

# Create your views here.
def home(request):
    return render(request, "index.html")

def science(request):
    return render(request, "science.html")

def tracker(request):
    return render(request, "tracker.html")

def assessment(request):
    return render(request, "assessment.html")

def advice(request):
    return render(request, "advice.html")

def community(request):
    return render(request, "community.html")

def profile(request):
    return render(request, "profile.html")

def blog_details(request):
    return render(request, "blog-details.html")

def ai_assistant(request):
    return render(request, "ai-assistant.html")

def forum_topic(request):
    return render(request, "forum-topic.html")

from .models import User
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
def login(request):
    if request.method == 'POST':
        try:
            data = request.POST
            phone = data.get('phone')
            password = data.get('password')
            
            if not all([phone, password]):
                return JsonResponse({'success': False, 'message': '请填写手机号和密码'})
                
            user = User.objects.filter(phone_number=phone).first()
            if not user:
                return JsonResponse({'success': False, 'message': '用户不存在'})
                
            if not check_password(password, user.password):
                return JsonResponse({'success': False, 'message': '密码错误'})
                
            # 手动设置session
            request.session['user_id'] = user.user_id
            request.session['is_authenticated'] = True
            
            return JsonResponse({
                'success': True,
                'message': '登录成功',
                'user': {
                    'id': user.user_id,
                    'name': user.user_name,
                    'email': user.email
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效请求方法'})

def check_session(request):
    if request.method == 'GET':
        is_authenticated = request.session.get('is_authenticated', False)
        user_id = request.session.get('user_id')
        
        if is_authenticated and user_id:
            user = User.objects.filter(user_id=user_id).first()
            if user:
                return JsonResponse({
                    'isAuthenticated': True,
                    'user': {
                        'id': user.user_id,
                        'name': user.user_name,
                        'email': user.email
                    }
                })
        
        return JsonResponse({'isAuthenticated': False})

def logout(request):
    # 清除session
    request.session.flush()
    return JsonResponse({'success': True, 'message': '登出成功'})

def register(request):
    if request.method == 'POST':
        try:
            data = request.POST
            phone = data.get('phone')
            password = data.get('password')
            name = data.get('name')
            email = data.get('email')
            
            # 验证必填字段
            if not all([phone, password, name, email]):
                return JsonResponse({'success': False, 'message': '请填写所有必填字段'})
                
            # 检查手机号是否已存在
            if User.objects.filter(phone_number=phone).exists():
                return JsonResponse({'success': False, 'message': '手机号已注册'})
                
            # 检查邮箱是否已存在
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': '邮箱已注册'})
                
            # 获取当前最大user_id并加1
            max_id = User.objects.all().order_by('-user_id').first()
            if max_id:
                new_id = str(int(max_id.user_id) + 1).zfill(10)  # 保持10位长度
            else:
                new_id = '1000000000'  # 初始ID
            
            # 创建用户
            user = User.objects.create(
                user_id=new_id,
                phone_number=phone,
                password=make_password(password),
                user_name=name,
                email=email,
                user_type='1'  # 普通用户
            )
            
            return JsonResponse({'success': True, 'message': '注册成功'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效请求方法'})
