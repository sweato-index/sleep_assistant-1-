from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import User, Document, DocComment
from django.contrib.auth.hashers import make_password, check_password
import json

def get_all_user_ids(request):
    user_ids = list(User.objects.values_list('user_id', flat=True))
    user_names = list(User.objects.values_list('user_name', flat=True))
    user_emails = list(User.objects.values_list('email', flat=True))
    return JsonResponse({'user_ids': user_ids, 'user_names': user_names, 'user_emails': user_emails})

# 论坛帖子列表
@require_http_methods(["GET"])
def forum_posts(request):
    posts = Document.objects.filter(doc_type='1').order_by('-doc_id')[:20]
    posts_data = []
    for post in posts:
        if post.create_time:
            local_time = timezone.localtime(post.create_time)
            time_str = local_time.strftime('%Y-%m-%d %H:%M')
        else:
            time_str = '未知时间'
        posts_data.append({
            'id': post.doc_id,
            'title': post.title,
            'summary': post.summary,
            'author': post.post_user.user_name,
            'create_time': time_str,
            'comment_count': DocComment.objects.filter(doc=post).count()
        })
    return JsonResponse({'posts': posts_data})

# 创建新帖子
@require_http_methods(["POST"])
def create_post(request):
    try:
        data = json.loads(request.body)
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        title = data.get('title')
        content = data.get('content')
        
        if not all([title, content]):
            return JsonResponse({'success': False, 'message': '标题和内容不能为空'}, status=400)
            
        # 生成新doc_id
        last_doc = Document.objects.order_by('-doc_id').first()
        new_id = str(int(last_doc.doc_id) + 1).zfill(10) if last_doc else '1000000000'
        
        post = Document.objects.create(
            doc_id=new_id,
            doc_type='1',  # 论坛帖子
            post_user=user,
            title=title,
            text=content,
            summary=content[:30] + '...' if len(content) > 30 else content
        )
        
        return JsonResponse({
            'success': True,
            'message': '帖子创建成功',
            'post_id': post.doc_id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 帖子详情
@require_http_methods(["GET"])
def post_detail(request, post_id):
    try:
        post = get_object_or_404(Document, doc_id=post_id, doc_type='1')
        comments = DocComment.objects.filter(doc=post).order_by('create_time')
        
        post_data = {
            'id': post.doc_id,
            'title': post.title,
            'content': post.text,
            'author': post.post_user.user_name,
            'create_time': timezone.localtime(post.create_time).strftime('%Y-%m-%d %H:%M'),
            'comments': [{
                'id': comment.comment_id,
                'author': comment.user.user_name,
                'content': comment.comment,
                'create_time': timezone.localtime(comment.create_time).strftime('%Y-%m-%d %H:%M')
            } for comment in comments]
        }
        return JsonResponse(post_data)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 添加评论
@require_http_methods(["POST"])
def add_comment(request, post_id):
    try:
        data = json.loads(request.body)
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        post = get_object_or_404(Document, doc_id=post_id)
        content = data.get('content')
        
        if not content:
            return JsonResponse({'success': False, 'message': '评论内容不能为空'}, status=400)
            
        # 生成新comment_id
        last_comment = DocComment.objects.order_by('-comment_id').first()
        new_id = str(int(last_comment.comment_id) + 1).zfill(10) if last_comment else '1000000000'
        
        comment = DocComment.objects.create(
            comment_id=new_id,
            doc=post,
            user=user,
            comment=content
        )
        
        return JsonResponse({
            'success': True,
            'message': '评论添加成功',
            'comment': {
                'id': comment.comment_id,
                'author': user.user_name,
                'content': comment.comment,
                'create_time': comment.create_time.strftime('%Y-%m-%d %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 基本视图函数保持不变
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

# 用户认证相关视图保持不变
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
            
            if not all([phone, password, name, email]):
                return JsonResponse({'success': False, 'message': '请填写所有必填字段'})
                
            if User.objects.filter(phone_number=phone).exists():
                return JsonResponse({'success': False, 'message': '手机号已注册'})
                
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': '邮箱已注册'})
                
            max_id = User.objects.all().order_by('-user_id').first()
            if max_id:
                new_id = str(int(max_id.user_id) + 1).zfill(10)
            else:
                new_id = '1000000000'
            
            user = User.objects.create(
                user_id=new_id,
                phone_number=phone,
                password=make_password(password),
                user_name=name,
                email=email,
                user_type='1'
            )
            
            return JsonResponse({'success': True, 'message': '注册成功'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效请求方法'})
