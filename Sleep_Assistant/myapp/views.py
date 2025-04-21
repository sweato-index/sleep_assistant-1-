from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import User, Document, DocComment, DocUserAction,AiQa
from django.db import transaction
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
        user_id = request.session.get('user_id')
        post = get_object_or_404(Document, doc_id=post_id, doc_type='1')
        
        # 确保post_user存在
        if not hasattr(post, 'post_user'):
            return JsonResponse({'success': False, 'message': '帖子作者信息缺失'}, status=500)
            
        # 获取所有评论并按创建时间排序
        all_comments = DocComment.objects.filter(doc=post).order_by('create_time')
        
        # 构建评论树
        def build_comment_tree(comments, parent=None):
            tree = []
            for comment in comments:
                if (comment.parent == parent if parent else comment.parent is None):
                    comment_data = {
                        'id': comment.comment_id,
                        'author': comment.user.user_name if hasattr(comment.user, 'user_name') else '未知用户',
                        'content': comment.comment,
                        'create_time': timezone.localtime(comment.create_time).strftime('%Y-%m-%d %H:%M') if comment.create_time else '未知时间',
                        'reply_count': DocComment.objects.filter(parent=comment).count(),
                        'replies': build_comment_tree(comments, comment)
                    }
                    tree.append(comment_data)
            return tree
        
        # 获取用户对该帖子的操作状态
        user_actions = {}
        if user_id:
            try:
                actions = DocUserAction.objects.filter(doc=post, user__user_id=user_id)
                user_actions = {
                    'liked': actions.filter(action_type='0').exists(),
                    'favorited': actions.filter(action_type='1').exists()
                }
            except Exception as e:
                print(f"获取用户操作状态错误: {str(e)}")
        
        try:
            post_data = {
                'success': True,
                'title': post.title,
                'content': post.text,
                'author': post.post_user.user_name if hasattr(post.post_user, 'user_name') else '未知用户',
                'create_time': timezone.localtime(post.create_time).strftime('%Y-%m-%d %H:%M') if post.create_time else '未知时间',
                'like_count': DocUserAction.objects.filter(doc=post, action_type='0').count(),
                'favorite_count': DocUserAction.objects.filter(doc=post, action_type='1').count(),
                'user_actions': user_actions or {},
                'comments': build_comment_tree(all_comments)
            }
            return JsonResponse(post_data)
        except Exception as e:
            print(f"构建响应数据错误: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '获取帖子详情失败',
                'error': str(e)
            }, status=500)
        return JsonResponse(post_data)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 评论和互动功能
@require_http_methods(["POST"])
def toggle_like(request, post_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        post = get_object_or_404(Document, doc_id=post_id)
        user = get_object_or_404(User, user_id=user_id)
        
        # 生成新action_id
        last_action = DocUserAction.objects.order_by('-action_id').first()
        new_id = str(int(last_action.action_id) + 1).zfill(10) if last_action else '1000000000'
        
        action, created = DocUserAction.objects.update_or_create(
            action_id=new_id,
            doc=post,
            user=user,
            action_type='0',  # 0=点赞
            defaults={'create_time': timezone.now()}
        )
        
        if not created:
            action.delete()
            
        return JsonResponse({
            'success': True,
            'liked': created,
            'like_count': DocUserAction.objects.filter(doc=post, action_type='0').count()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])        
def toggle_favorite(request, post_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        post = get_object_or_404(Document, doc_id=post_id)
        user = get_object_or_404(User, user_id=user_id)
        
        # 生成新action_id
        last_action = DocUserAction.objects.order_by('-action_id').first()
        new_id = str(int(last_action.action_id) + 1).zfill(10) if last_action else '1000000000'
        
        action, created = DocUserAction.objects.update_or_create(
            action_id=new_id,
            doc=post,
            user=user,
            action_type='1',  # 1=收藏
            defaults={'create_time': timezone.now()}
        )
        
        if not created:
            action.delete()
            
        return JsonResponse({
            'success': True,
            'favorited': created,
            'favorite_count': DocUserAction.objects.filter(doc=post, action_type='1').count()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])
def add_comment(request, post_id):
    try:
        print(f"收到评论请求，post_id: {post_id}")  # 调试日志
        data = json.loads(request.body)
        print(f"请求数据: {data}")  # 调试日志
        
        user_id = request.session.get('user_id')
        if not user_id:
            print("用户未登录")  # 调试日志
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        post = get_object_or_404(Document, doc_id=post_id)
        content = data.get('content')
        parent_id = data.get('parent_id')
        
        if not content:
            print("评论内容为空")  # 调试日志
            return JsonResponse({'success': False, 'message': '评论内容不能为空'}, status=400)
            
        # 生成新comment_id
        last_comment = DocComment.objects.order_by('-comment_id').first()
        new_id = str(int(last_comment.comment_id) + 1).zfill(10) if last_comment else '1000000000'
        print(f"生成comment_id: {new_id}")  # 调试日志
        
        # 处理父评论
        parent = None
        if parent_id:
            try:
                parent = DocComment.objects.get(comment_id=parent_id, doc=post)
            except DocComment.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '父评论不存在'
                }, status=400)
        
        # 创建评论
        try:
            comment = DocComment.objects.create(
                comment_id=new_id,
                doc=post,
                user=user,
                comment=content,
                create_time=timezone.now(),
                status='1',
                parent=parent
            )
            print(f"评论创建成功: {comment.comment_id}")  # 调试日志
            
        except Exception as e:
            print(f"创建评论失败: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '评论创建失败',
                'error': str(e)
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'message': '评论添加成功',
            'comment': {
                'id': comment.comment_id,
                'author': user.user_name,
                'content': comment.comment,
                'create_time': comment.create_time.strftime('%Y-%m-%d %H:%M'),
                'parent_id': parent_id if parent_id else None,
                'reply_count': 0
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

def forum_topic(request, post_id):
    return render(request, "forum-topic.html", {'post_id': post_id})

@require_http_methods(["POST"])
def save_ai_qa(request):
    try:
        print(f"Received request to save AI QA: {request.body}")  # Debug log
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '无效的JSON数据',
                'error': str(e)
            }, status=400)
            
        user_id = request.session.get('user_id')
        if not user_id:
            print("No user_id in session")  # Debug log
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        try:
            user = User.objects.get(user_id=user_id)
            print(f"Found user: {user.user_id}")  # Debug log
        except User.DoesNotExist:
            print(f"User not found: {user_id}")  # Debug log
            return JsonResponse({'success': False, 'message': '用户不存在'}, status=404)
        question = str(data.get('question', '')).strip()
        answer = str(data.get('answer', '')).strip()
        
        print(f"Question: {question[:50]}...")  # Debug log first 50 chars
        print(f"Answer: {answer[:50]}...")  # Debug log first 50 chars
        
        if not question or not answer:
            print("Empty question or answer")  # Debug log
            return JsonResponse({
                'success': False, 
                'message': '问题和回答不能为空',
                'received_data': {
                    'question_length': len(question),
                    'answer_length': len(answer)
                }
            }, status=400)
            
        # 生成新qa_id
        try:
            last_qa = AiQa.objects.order_by('-qa_id').first()
            if last_qa:
                new_id = str(int(last_qa.qa_id) + 1).zfill(10)
                print(f"Using incremented QA ID: {new_id}")  # Debug log
            else:
                new_id = '1000000000'
                print("Using default QA ID")  # Debug log
        except Exception as e:
            print(f"QA ID generation error: {str(e)}")
            new_id = str(int(timezone.now().timestamp()))[-10:].ljust(10, '0')
            print(f"Using fallback QA ID: {new_id}")  # Debug log
        
        # 创建记录
        try:
            print("Attempting to create AiQa record")  # Debug log
            qa = AiQa(
                qa_id=new_id,
                user=user,
                qa_content=question[:1000],  # 确保不超过字段长度限制
                create_time=timezone.now(),
                answers=answer[:2000]  # 确保不超过字段长度限制
            )
            print("Created AiQa object, validating...")  # Debug log
            qa.full_clean()  # 验证模型字段
            print("Validation passed, saving...")  # Debug log
            qa.save()
            print(f"Successfully saved QA record with ID: {qa.qa_id}")  # Debug log
            
            return JsonResponse({
                'success': True,
                'message': '对话记录保存成功',
                'qa_id': qa.qa_id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': '保存对话记录失败',
                'error': str(e)
            }, status=500)
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

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
