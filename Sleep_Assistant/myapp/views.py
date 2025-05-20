from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import models
from .models import User, Document, DocComment, DocUserAction, AiQa, SleepGroup, UserGroup, ChatHistory,SleepRecord, UserChallenge, SleepChallenge
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
import json
import os
from datetime import datetime
from django.conf import settings
from django.views import View


def get_all_user_ids(request):
    user_ids = list(User.objects.values_list('user_id', flat=True))
    user_names = list(User.objects.values_list('user_name', flat=True))
    user_emails = list(User.objects.values_list('email', flat=True))
    return JsonResponse({'user_ids': user_ids, 'user_names': user_names, 'user_emails': user_emails})

#个人中心
@require_http_methods(["GET"])
def get_user_profile(request):
    user_id = request.session.get('user_id')  # 假设登录后 user_id 被存入 session
    if not user_id:
        return JsonResponse({'success': False, 'message': '未登录'}, status=401)

    user = get_object_or_404(User, user_id=user_id)

    user_info = {
        'user_id': user.user_id,
        'user_name': user.user_name or user.phone_number,
        'phone_number': user.phone_number,
        'email': user.email,
        'age': user.age,
        'gender': user.gender,
        'tag': user.tag,
        'description': user.description,
        'birthday': user.birthday.strftime('%Y-%m-%d') if user.birthday else '',
        'sleep_notice': user.sleep_notice,
        'wake_notice': user.wake_notice,
        'location': user.location,
        'avatar_url': user.avatar_url
    }

    return JsonResponse({'success': True, 'data': user_info})

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

# 群组功能视图
@require_http_methods(["POST"])
def create_group(request):
    try:
        data = json.loads(request.body)
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        group_name = data.get('group_name')
        description = data.get('description', '')
        
        if not group_name:
            return JsonResponse({'success': False, 'message': '群组名称不能为空'}, status=400)
            
        # 生成新group_id
        last_group = SleepGroup.objects.order_by('-group_id').first()
        new_id = str(int(last_group.group_id) + 1).zfill(10) if last_group else '1000000000'
        
        group = SleepGroup.objects.create(
            group_id=new_id,
            group_name=group_name,
            owner=user,
            description=description
        )
        
        # 自动将创建者加入群组
        UserGroup.objects.create(
            group=group,
            member=user,
            role='1'  # 管理员
        )
        
        return JsonResponse({
            'success': True,
            'message': '群组创建成功',
            'group_id': group.group_id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["GET"])
def get_groups(request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        # 获取用户加入的群组
        user_groups = UserGroup.objects.filter(member__user_id=user_id).select_related('group')
        groups_data = []
        for ug in user_groups:
            group = ug.group
            groups_data.append({
                'group_id': group.group_id,
                'group_name': group.group_name,
                'description': group.description,
                'member_count': UserGroup.objects.filter(group=group).count(),
                'role': ug.role,
                'create_time': group.create_time.strftime('%Y-%m-%d %H:%M')
            })
            
        # 获取公开群组(用户未加入的)
        all_groups = SleepGroup.objects.filter(status='1').exclude(
            group_id__in=[g.group.group_id for g in user_groups]
        )
        for group in all_groups:
            groups_data.append({
                'group_id': group.group_id,
                'group_name': group.group_name,
                'description': group.description,
                'member_count': UserGroup.objects.filter(group=group).count(),
                'role': None,  # 未加入
                'create_time': group.create_time.strftime('%Y-%m-%d %H:%M')
            })
            
        return JsonResponse({
            'success': True,
            'groups': groups_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])
def join_group(request, group_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        group = get_object_or_404(SleepGroup, group_id=group_id)
        
        # 检查是否已加入
        if UserGroup.objects.filter(group=group, member=user).exists():
            return JsonResponse({'success': False, 'message': '您已加入该群组'}, status=400)
            
        UserGroup.objects.create(
            group=group,
            member=user,
            role='0'  # 普通成员
        )
        
        return JsonResponse({
            'success': True,
            'message': '加入群组成功'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])
def leave_group(request, group_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        group = get_object_or_404(SleepGroup, group_id=group_id)
        
        # 检查是否是群主
        if group.owner.user_id == user_id:
            return JsonResponse({'success': False, 'message': '群主不能退出群组'}, status=400)
            
        UserGroup.objects.filter(group=group, member=user).delete()
        
        return JsonResponse({
            'success': True,
            'message': '退出群组成功'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["GET"])
def get_group_chat(request, group_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        # 检查用户是否在群组中
        if not UserGroup.objects.filter(group__group_id=group_id, member__user_id=user_id).exists():
            return JsonResponse({'success': False, 'message': '您不在该群组中'}, status=403)
            
        # 获取群组信息
        group = get_object_or_404(SleepGroup, group_id=group_id)
        members = UserGroup.objects.filter(group=group).select_related('member')
        
        # 获取聊天记录(最近100条)
        messages = ChatHistory.objects.filter(group=group).order_by('-create_time')[:100]
        
        return JsonResponse({
            'success': True,
            'group': {
                'group_id': group.group_id,
                'group_name': group.group_name,
                'description': group.description,
                'owner': group.owner.user_name
            },
            'members': [{
                'user_id': m.member.user_id,
                'user_name': m.member.user_name,
                'role': m.role
            } for m in members],
            'messages': [{
                'id': msg.id,
                'user_id': msg.member.user_id,
                'user_name': msg.member.user_name,
                'content': msg.content,
                'msg_type': msg.msg_type,
                'create_time': msg.create_time.strftime('%Y-%m-%d %H:%M')
            } for msg in messages]
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])
def send_group_message(request, group_id):
    try:
        data = json.loads(request.body)
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        # 检查用户是否在群组中
        if not UserGroup.objects.filter(group__group_id=group_id, member__user_id=user_id).exists():
            return JsonResponse({'success': False, 'message': '您不在该群组中'}, status=403)
            
        user = get_object_or_404(User, user_id=user_id)
        group = get_object_or_404(SleepGroup, group_id=group_id)
        content = data.get('content')
        msg_type = data.get('msg_type', '0')
        
        if not content:
            return JsonResponse({'success': False, 'message': '消息内容不能为空'}, status=400)
            
        # 创建消息记录
        message = ChatHistory.objects.create(
            group=group,
            member=user,
            content=content,
            msg_type=msg_type
        )
        
        return JsonResponse({
            'success': True,
            'message': '消息发送成功',
            'message_id': message.id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 基本视图函数保持不变
def home(request):
    return render(request, "index.html")

@require_http_methods(["GET"])
def science_posts(request):
    """获取知识中心文章列表"""
    try:
        # 获取排序参数 (默认按最新排序)
        sort_by = request.GET.get('sort', 'newest')
        
        # 构建查询
        posts_query = Document.objects.filter(doc_type='3')
        
        # 应用排序
        if sort_by == 'popular':
            posts_query = posts_query.annotate(
                like_count=models.Count('docuseraction', filter=models.Q(docuseraction__action_type='0')))
            posts_query = posts_query.order_by('-like_count', '-create_time')
        else:  # newest
            posts_query = posts_query.order_by('-create_time')
            
        posts = posts_query[:20]
        
        # 获取用户ID用于检查点赞状态
        user_id = request.session.get('user_id')
        
        posts_data = []
        for post in posts:
            # 检查用户是否点赞过该文章
            liked = False
            if user_id:
                liked = DocUserAction.objects.filter(
                    doc=post, 
                    user__user_id=user_id,
                    action_type='0'
                ).exists()
                
            posts_data.append({
                'id': post.doc_id,
                'title': post.title,
                'summary': post.summary,
                'author': post.post_user.user_name if hasattr(post.post_user, 'user_name') else '匿名用户',
                'author_id': post.post_user.user_id,
                'create_time': timezone.localtime(post.create_time).strftime('%Y-%m-%d %H:%M') if post.create_time else '未知时间',
                'comment_count': DocComment.objects.filter(doc=post).count(),
                'like_count': DocUserAction.objects.filter(doc=post, action_type='0').count(),
                'liked': liked
            })
            
        return JsonResponse({
            'success': True,
            'posts': posts_data,
            'sort': sort_by
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def create_science_post(request):
    """创建知识中心文章"""
    try:
        print("Raw request data:", request.body)
        print("Request content type:", request.content_type)
        print("Request POST data:", request.POST)
        print("Request FILES data:", request.FILES)
        
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        
        # 从FormData获取字段
        title = request.POST.get('title', '').strip()
        content = request.POST.get('text', '').strip()  # 注意字段名是text不是content
        summary = request.POST.get('summary', '').strip()
        doc_type = request.POST.get('doc_type', '3')
        
        print("Extracted values:", {
            'title': title,
            'content': content,
            'summary': summary,
            'doc_type': doc_type
        })
        
        # 验证输入
        if not title or not content:
            return JsonResponse({
                'success': False, 
                'message': '标题和内容不能为空',
                'received_data': {
                    'title': title,
                    'content': content
                }
            }, status=400)
            
        # 确保内容长度不超过数据库限制
        if len(title) > 200:
            return JsonResponse({
                'success': False,
                'message': '标题过长，请控制在200字符以内'
            }, status=400)
            
        if len(content) > 10000:
            return JsonResponse({
                'success': False,
                'message': '内容过长，请控制在10000字符以内'
            }, status=400)
            
        # 生成新doc_id
        last_doc = Document.objects.order_by('-doc_id').first()
        new_id = str(int(last_doc.doc_id) + 1).zfill(10) if last_doc else '1000000000'
        
        # 创建文章
        post = Document.objects.create(
            doc_id=new_id,
            doc_type=doc_type,  # 使用传入的doc_type
            post_user=user,
            title=title,
            text=content,
            summary=summary if summary else content[:100] + '...',
            create_time=timezone.now()
        )
        
        # 处理图片上传
        if 'image' in request.FILES:
            image = request.FILES['image']
            # 确保上传目录存在
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'science_posts')
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成文件名
            ext = os.path.splitext(image.name)[1]
            filename = f'post_{new_id}{ext}'
            file_path = os.path.join(upload_dir, filename)
            
            # 保存文件
            with open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
            # 更新文章图片URL
            post.image_url = f'science_posts/{filename}'
            post.save()
        
        # 返回完整的文章信息
        return JsonResponse({
            'success': True,
            'message': '文章创建成功',
            'post': {
                'id': post.doc_id,
                'title': post.title,
                'summary': post.summary,
                'author': user.user_name,
                'author_id': user.user_id,
                'create_time': timezone.localtime(post.create_time).strftime('%Y-%m-%d %H:%M'),
                'comment_count': 0,
                'like_count': 0,
                'liked': False,
                'image_url': post.image_url if hasattr(post, 'image_url') else None
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["GET"])
def science_post_detail(request, post_id):
    """获取知识中心文章详情"""
    try:
        user_id = request.session.get('user_id')
        post = get_object_or_404(Document, doc_id=post_id, doc_type='3')
        
        # 检查用户是否点赞过该文章
        liked = False
        if user_id:
            liked = DocUserAction.objects.filter(
                doc=post, 
                user__user_id=user_id,
                action_type='0'
            ).exists()
        
        post_data = {
            'post': {
                'id': post.doc_id,
                'title': post.title,
                'text': post.text,
                'summary': post.summary,
                'author': post.post_user.user_name if hasattr(post.post_user, 'user_name') else '匿名用户',
                'create_time': timezone.localtime(post.create_time).strftime('%Y-%m-%d %H:%M') if post.create_time else '未知时间',
                'like_count': DocUserAction.objects.filter(doc=post, action_type='0').count(),
                'comment_count': DocComment.objects.filter(doc=post).count(),
                'image': post.image_url if hasattr(post, 'image_url') else '/static/img/blog-1.png',
                'liked': liked
            }
        }
        return JsonResponse(post_data)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["GET"])
def popular_science_posts(request):
    """获取热门知识文章"""
    try:
        # 获取点赞数最高的5篇文章
        posts = Document.objects.filter(doc_type='3').annotate(
            like_count=models.Count('docuseraction', filter=models.Q(docuseraction__action_type='0')))
        posts = posts.order_by('-like_count', '-create_time')[:5]
        
        posts_data = []
        for post in posts:
            posts_data.append({
                'id': post.doc_id,
                'title': post.title,
                'like_count': post.like_count,
                'image': post.image_url if hasattr(post, 'image_url') else '/static/img/blog-1.png'
            })
            
        return JsonResponse({
            'posts': posts_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])
def toggle_science_like(request, post_id):
    """点赞/取消点赞知识文章"""
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        post = get_object_or_404(Document, doc_id=post_id, doc_type='3')
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
def add_science_comment(request, post_id):
    """添加知识文章评论"""
    try:
        data = json.loads(request.body)
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        post = get_object_or_404(Document, doc_id=post_id, doc_type='3')
        content = data.get('content')
        parent_id = data.get('parent_id')
        
        if not content:
            return JsonResponse({'success': False, 'message': '评论内容不能为空'}, status=400)
            
        # 生成新comment_id
        last_comment = DocComment.objects.order_by('-comment_id').first()
        new_id = str(int(last_comment.comment_id) + 1).zfill(10) if last_comment else '1000000000'
        
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
        comment = DocComment.objects.create(
            comment_id=new_id,
            doc=post,
            user=user,
            comment=content,
            create_time=timezone.now(),
            status='1',
            parent=parent
        )
        
        return JsonResponse({
            'success': True,
            'message': '评论添加成功',
            'comment': {
                'id': comment.comment_id,
                'author': user.user_name,
                'author_id': user.user_id,
                'content': comment.comment,
                'create_time': comment.create_time.strftime('%Y-%m-%d %H:%M'),
                'parent_id': parent_id if parent_id else None,
                'reply_count': 0
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def science(request):
    """知识中心主页面"""
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
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    user = get_object_or_404(User, user_id=user_id)
    context = {
        'user': user,
        'user_name': user.user_name or user.phone_number,
        'phone_number': user.phone_number,
        'email': user.email,
        'age': user.age,
        'gender': user.gender,
        'tag': user.tag,
        'description': user.description,
        'birthday': user.birthday.strftime('%Y-%m-%d') if user.birthday else '',
        'sleep_notice': user.sleep_notice,
        'wake_notice': user.wake_notice,
    }
    return render(request, 'profile.html', context)


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
                
            # 更新最后登录时间
            user.last_login = timezone.now()
            user.save()
            
            request.session['user_id'] = user.user_id
            request.session['is_authenticated'] = True
            request.session['user_type'] = user.user_type
            
            response_data = {
                'success': True,
                'message': '登录成功',
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else '首次登录',
                'user': {
                    'id': user.user_id,
                    'name': user.user_name,
                    'email': user.email,
                    'user_type': str(user.user_type)  # 确保user_type是字符串
                },
                'redirect_url': '/api/admin/dashboard/' if str(user.user_type) == '0' else '/'
            }
            # 确保重定向URL正确
            print(f"Login redirect URL: {response_data['redirect_url']}")  # 调试日志
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': '无效请求方法'})

# 专家问答功能视图
@require_http_methods(["GET"])
def expert_questions(request):
    """获取专家问答列表"""
    try:
        questions = Document.objects.filter(doc_type='2').order_by('-create_time')[:20]
        questions_data = []
        for q in questions:
            questions_data.append({
                'id': q.doc_id,
                'title': q.title,
                'summary': q.summary,
                'author': q.post_user.user_name if hasattr(q.post_user, 'user_name') else '匿名用户',
                'create_time': timezone.localtime(q.create_time).strftime('%Y-%m-%d %H:%M') if q.create_time else '未知时间',
                'answered': bool(q.text)  # 是否有专家回答
            })
        return JsonResponse({'questions': questions_data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])
def create_question(request):
    """用户提交新问题"""
    try:
        print("Received create_question request")  # Debug log
        try:
            data = json.loads(request.body)
            print(f"Request data: {data}")  # Debug log
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '无效的JSON数据',
                'error': str(e)
            }, status=400)
            
        user_id = request.session.get('user_id')
        if not user_id:
            print("User not logged in")  # Debug log
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        try:
            user = User.objects.get(user_id=user_id)
            print(f"Found user: {user.user_id}")  # Debug log
        except User.DoesNotExist:
            print(f"User not found: {user_id}")  # Debug log
            return JsonResponse({'success': False, 'message': '用户不存在'}, status=404)
            
        title = str(data.get('title', '')).strip()
        summary = str(data.get('summary', '')).strip()
        
        print(f"Title: {title}")  # Debug log
        print(f"Summary: {summary}")  # Debug log
        
        if not title or not summary:
            print("Title or summary is empty")  # Debug log
            return JsonResponse({
                'success': False, 
                'message': '标题和问题描述不能为空',
                'received_data': {
                    'title_length': len(title),
                    'summary_length': len(summary)
                }
            }, status=400)
            
        # 生成新doc_id
        try:
            last_doc = Document.objects.order_by('-doc_id').first()
            if last_doc:
                new_id = str(int(last_doc.doc_id) + 1).zfill(10)
                print(f"Using incremented doc_id: {new_id}")  # Debug log
            else:
                new_id = '1000000000'
                print("Using default doc_id")  # Debug log
        except Exception as e:
            print(f"doc_id generation error: {str(e)}")
            new_id = str(int(timezone.now().timestamp()))[-10:].ljust(10, '0')
            print(f"Using fallback doc_id: {new_id}")  # Debug log
        
        # 创建问题记录
        try:
            print("Attempting to create Document record")  # Debug log
            question = Document(
                doc_id=new_id,
                doc_type='2',  # 专家问答
                post_user=user,
                title=title,
                summary=summary,
                text='',  # 设置空字符串默认值
                create_time=timezone.now()
            )
            print("Created Document object, validating...")  # Debug log
            question.full_clean()  # 验证模型字段
            print("Validation passed, saving...")  # Debug log
            question.save()
            print(f"Successfully saved question with ID: {question.doc_id}")  # Debug log
            
            return JsonResponse({
                'success': True,
                'message': '问题提交成功',
                'question_id': question.doc_id
            })
            
        except Exception as e:
            print(f"Error creating question: {str(e)}")  # Debug log
            return JsonResponse({
                'success': False,
                'message': '问题提交失败',
                'error': str(e)
            }, status=500)
            
    except Exception as e:
        print(f"Unexpected error in create_question: {str(e)}")  # Debug log
        return JsonResponse({
            'success': False,
            'message': '服务器内部错误',
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def question_detail(request, question_id):
    """获取问题详情"""
    try:
        question = get_object_or_404(Document, doc_id=question_id, doc_type='2')
        
        return JsonResponse({
            'success': True,
            'title': question.title,
            'summary': question.summary,
            'answer': question.text,
            'author': question.post_user.user_name if hasattr(question.post_user, 'user_name') else '匿名用户',
            'create_time': timezone.localtime(question.create_time).strftime('%Y-%m-%d %H:%M') if question.create_time else '未知时间',
            'answered': bool(question.text)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])
def answer_question(request, question_id):
    """专家回答问题"""
    try:
        print(f"Received answer request for question {question_id}")  # Debug log
        data = json.loads(request.body)
        user_id = request.session.get('user_id')
        print(f"User ID from session: {user_id}")  # Debug log
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        # 检查用户是否是专家
        user = get_object_or_404(User, user_id=user_id)
        print(f"User type: {user.user_type}")  # Debug log
        if user.user_type != '2':  # 假设2是专家用户类型
            print(f"User {user_id} is not an expert (type={user.user_type})")  # Debug log
            return JsonResponse({'success': False, 'message': '只有专家可以回答问题'}, status=403)
            
        answer = data.get('answer')
        print(f"Answer content length: {len(answer) if answer else 0}")  # Debug log
        if not answer:
            return JsonResponse({'success': False, 'message': '回答内容不能为空'}, status=400)
            
        question = get_object_or_404(Document, doc_id=question_id, doc_type='2')
        if question.text:
            return JsonResponse({'success': False, 'message': '该问题已有回答'}, status=400)
            
        question.text = answer
        question.save()
        
        return JsonResponse({
            'success': True,
            'message': '回答提交成功'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

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
                        'email': user.email,
                        'user_type': str(user.user_type)  # 确保user_type是字符串
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

@csrf_exempt
def update_user_profile(request):
    print("收到更新用户资料的请求")
    print("请求方法:", request.method)
    print("POST数据:", request.POST)
    print("FILES数据:", request.FILES)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '只支持POST请求'}, status=405)

    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': '未登录'}, status=401)

    try:
        user = User.objects.get(user_id=user_id)
        print("找到用户:", user.user_id)
        
        # 更新基本信息
        if 'user_name' in request.POST:
            user.user_name = request.POST['user_name']
            print("更新用户名:", user.user_name)
        if 'email' in request.POST:
            user.email = request.POST['email']
            print("更新邮箱:", user.email)
        if 'gender' in request.POST:
            # 将性别值转换为对应的数字代码
            gender_map = {'male': '0', 'female': '1', 'other': '2'}
            gender_value = request.POST['gender'].lower()
            user.gender = gender_map.get(gender_value, '2')  # 默认为"其他"
            print("更新性别:", user.gender)
        if 'birthday' in request.POST:
            try:
                user.birthday = datetime.strptime(request.POST['birthday'], '%Y-%m-%d')
                print("更新生日:", user.birthday)
            except ValueError:
                return JsonResponse({'success': False, 'message': '生日格式错误'}, status=400)
        if 'description' in request.POST:
            user.description = request.POST['description']
            print("更新描述:", user.description)
        if 'tag' in request.POST:
            user.tag = request.POST['tag']
            print("更新标签:", user.tag)
        if 'location' in request.POST:
            user.location = request.POST['location']
            print("更新所在地:", user.location)

        # 处理头像上传
        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            print("处理头像上传:", avatar.name)
            
            # 检查文件类型
            if not avatar.content_type.startswith('image/'):
                return JsonResponse({'success': False, 'message': '只支持图片文件'}, status=400)
            
            # 生成文件名
            ext = os.path.splitext(avatar.name)[1]
            filename = f'avatar_{user_id}{ext}'
            
            # 确保上传目录存在
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
            os.makedirs(upload_dir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, 'wb+') as destination:
                for chunk in avatar.chunks():
                    destination.write(chunk)
            
            # 更新用户头像URL（使用相对路径）
            user.avatar_url = f'avatars/{filename}'
            print("更新头像URL:", user.avatar_url)

        print("保存用户信息")
        user.save()
        print("用户信息保存成功")
        
        return JsonResponse({
            'success': True,
            'message': '更新成功',
            'data': {
                'user_name': user.user_name,
                'email': user.email,
                'gender': user.gender,
                'birthday': user.birthday.strftime('%Y-%m-%d') if user.birthday else None,
                'description': user.description,
                'tag': user.tag,
                'location': user.location,
                'avatar_url': user.avatar_url
            }
        })
    except User.DoesNotExist:
        print("用户不存在:", user_id)
        return JsonResponse({'success': False, 'message': '用户不存在'}, status=404)
    except Exception as e:
        print("更新用户资料时发生错误:", str(e))
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])
def save_reminder_settings(request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        data = json.loads(request.body)
        sleep_time = data.get('sleep_time')
        wake_time = data.get('wake_time')
        browser_notification = data.get('browser_notification', False)
        email_notification = data.get('email_notification', False)
        
        user = get_object_or_404(User, user_id=user_id)
        user.sleep_notice = sleep_time
        user.wake_notice = wake_time
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': '提醒设置保存成功',
            'data': {
                'sleep_notice': user.sleep_notice,
                'wake_notice': user.wake_notice
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["POST"])
def delete_account(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': '未登录'}, status=401)

    try:
        with transaction.atomic():
            # 获取用户对象
            user = get_object_or_404(User, user_id=user_id)
            
            # 删除用户相关的所有数据
            # 1. 删除睡眠记录
            SleepRecord.objects.filter(user=user).delete()
            
            # 2. 删除用户参与的挑战
            UserChallenge.objects.filter(user=user).delete()
            
            # 3. 删除用户创建的挑战
            SleepChallenge.objects.filter(initiator=user).delete()
            
            # 4. 删除用户加入的群组
            UserGroup.objects.filter(user=user).delete()
            
            # 5. 删除用户创建的群组
            SleepGroup.objects.filter(owner=user).delete()
            
            # 6. 删除用户的聊天记录
            ChatHistory.objects.filter(user=user).delete()
            
            # 7. 删除用户的AI问答记录
            AiQa.objects.filter(user=user).delete()
            
            # 8. 删除用户的文档评论
            DocComment.objects.filter(user=user).delete()
            
            # 9. 删除用户的文档操作记录
            DocUserAction.objects.filter(user=user).delete()
            
            # 10. 最后删除用户本身
            user.delete()
            
            # 清除session
            request.session.flush()
            
            return JsonResponse({
                'success': True,
                'message': '账号已成功注销'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'注销账号失败：{str(e)}'
        }, status=500)

from django.contrib.auth.decorators import login_required

# 内容管理
@require_http_methods(["GET", "POST"])
def manage_content(request):
    # 检查管理员权限
    if not request.session.get('is_authenticated'):
        return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
        
    if request.session.get('user_type') != '0':  # 0表示管理员
        return JsonResponse({'success': False, 'message': '无权限访问'}, status=403)

    if request.method == 'GET':
        try:
            print("开始获取内容管理数据")  # 调试日志
            
            # 获取论坛帖子
            posts = Document.objects.filter(doc_type='1').order_by('-create_time')[:50]
            print(f"找到{len(posts)}篇帖子")  # 调试日志
            
            posts_data = []
            for post in posts:
                try:
                    author_name = post.post_user.user_name if hasattr(post.post_user, 'user_name') else '匿名用户'
                    create_time = timezone.localtime(post.create_time).strftime('%Y-%m-%d %H:%M') if post.create_time else '未知时间'
                    
                    posts_data.append({
                        'id': post.doc_id,
                        'title': post.title,
                        'author': author_name,
                        'create_time': create_time
                    })
                except Exception as e:
                    print(f"处理帖子{post.doc_id}时出错: {str(e)}")  # 调试日志
                    continue

            # 获取专家问答
            questions = Document.objects.filter(doc_type='2').order_by('-create_time')[:50]
            print(f"找到{len(questions)}个问题")  # 调试日志
            
            questions_data = []
            for q in questions:
                try:
                    author_name = q.post_user.user_name if hasattr(q.post_user, 'user_name') else '匿名用户'
                    create_time = timezone.localtime(q.create_time).strftime('%Y-%m-%d %H:%M') if q.create_time else '未知时间'
                    
                    questions_data.append({
                        'id': q.doc_id,
                        'title': q.title,
                        'author': author_name,
                        'create_time': create_time,
                        'answered': bool(q.text)
                    })
                except Exception as e:
                    print(f"处理问题{q.doc_id}时出错: {str(e)}")  # 调试日志
                    continue

            response_data = {
                'success': True,
                'posts': posts_data,
                'questions': questions_data
            }
            print("成功获取内容管理数据")  # 调试日志
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            content_id = data.get('content_id')
            content_type = data.get('content_type', 'post')  # 默认为帖子
            
            if not all([action, content_id]):
                return JsonResponse({'success': False, 'message': '缺少必要参数'}, status=400)

            content = get_object_or_404(Document, doc_id=content_id)
            
            if action == 'delete':
                content.delete()
                return JsonResponse({'success': True, 'message': '内容删除成功'})
            elif action == 'approve':
                content.status = '1'  # 1表示已审核
                content.save()
                return JsonResponse({'success': True, 'message': '内容审核通过'})
            elif action == 'reject':
                content.status = '2'  # 2表示已拒绝
                content.save()
                return JsonResponse({'success': True, 'message': '内容已拒绝'})
            else:
                return JsonResponse({'success': False, 'message': '无效的操作类型'}, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': '操作失败',
                'error': str(e)
            }, status=500)

# 系统设置
@require_http_methods(["GET", "POST"])
def system_settings(request):
    if request.method == 'GET':
        try:
            from django.conf import settings
            settings_data = {
                'site_name': getattr(settings, 'SITE_NAME', '睡眠助手'),
                'maintenance_mode': getattr(settings, 'MAINTENANCE_MODE', False),
                'allow_registration': getattr(settings, 'ALLOW_REGISTRATION', True),
                'default_user_type': getattr(settings, 'DEFAULT_USER_TYPE', '1'),
                'notification_settings': {
                    'email_enabled': getattr(settings, 'EMAIL_NOTIFICATIONS_ENABLED', True),
                    'push_enabled': getattr(settings, 'PUSH_NOTIFICATIONS_ENABLED', True)
                }
            }
            return JsonResponse({
                'success': True,
                'settings': settings_data
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 这里应该实现更新系统设置的逻辑
            # 注意：实际项目中应该使用更安全的方式更新设置
            
            return JsonResponse({
                'success': True,
                'message': '系统设置已更新'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 管理员仪表盘

def admin_dashboard(request):
    try:
        # 检查用户权限
        if not request.session.get('is_authenticated'):
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user_type = request.session.get('user_type')
        if user_type != '0':  # 0表示管理员
            return JsonResponse({'success': False, 'message': '无权限访问'}, status=403)
            
        # 获取系统统计数据
        total_users = User.objects.count()
        active_users = User.objects.filter(last_login__gte=timezone.now()-timezone.timedelta(days=30)).count()
        experts = User.objects.filter(user_type='2').count()
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'experts': experts
        }
        
        # 根据请求类型返回不同响应
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'stats': stats
            })
        else:
            return render(request, "admin.html", {
                'stats': stats
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 获取用户列表

@require_http_methods(["GET"])
def get_users(request):
    try:
        # 临时移除权限检查
            
        # 获取所有用户数据
        users = User.objects.all().order_by('-user_id')
        users_data = []
        for user in users:
            users_data.append({
                'id': user.user_id,
                'name': user.user_name,
                'email': user.email,
                'phone': user.phone_number,
                'type': user.user_type
            })
            
        return JsonResponse({
            'success': True,
            'users': users_data
        }, json_dumps_params={'ensure_ascii': False})  # 确保中文正常显示
        
    except Exception as e:
        import traceback
        traceback.print_exc()  # 打印完整错误堆栈
        return JsonResponse({
            'success': False,
            'message': '获取用户列表失败',
            'error': str(e)
        }, status=500)

# 更新用户信息
@require_http_methods(["GET", "POST"])
def update_user(request, user_id):
    if request.method == 'GET':
        try:
            user = get_object_or_404(User, user_id=user_id)
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.user_id,
                    'name': user.user_name,
                    'email': user.email,
                    'phone': user.phone_number,
                    'type': user.user_type
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
            
    elif request.method == 'POST':
        try:
            # 临时移除权限检查
                
            data = json.loads(request.body)
            user = get_object_or_404(User, user_id=user_id)
            
            # 更新用户信息
            if 'name' in data:
                user.user_name = data['name']
            if 'email' in data:
                user.email = data['email']
            if 'phone' in data:
                user.phone_number = data['phone']
            if 'type' in data:
                user.user_type = data['type']
                
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': '用户信息更新成功'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 删除用户
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    try:
        # 临时移除权限检查
            
        user = get_object_or_404(User, user_id=user_id)
        
        # 不能删除自己
        if user.user_id == request.session.get('user_id'):
            return JsonResponse({'success': False, 'message': '不能删除自己'}, status=400)
            
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': '用户删除成功'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def calendar_view(request):
    return render(request, 'sleep/calendar.html')

def get_sleep_data(request):
    records = SleepRecord.objects.all()
    events = [{
        'title': f"{r.hours}h (质量{r.quality})",
        'start': r.date.isoformat(),
        'extendedProps': {
            'hours': r.hours,
            'quality': r.quality
        }
    } for r in records]
    return JsonResponse(events, safe=False)

@csrf_exempt
def add_sleep_record(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        hours = float(data['hours'])
        quality = int(data['quality'])

        SleepRecord.objects.update_or_create(
            date=date,
            defaults={'hours': hours, 'quality': quality}
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid'}, status=400)