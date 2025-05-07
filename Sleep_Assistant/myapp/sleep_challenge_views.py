from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from .models import User, SleepChallenge, UserChallenge, ChallengeCheckIn
import json
import time
from django.db import IntegrityError
from datetime import timedelta

# 获取挑战列表
@require_http_methods(["GET"])
def get_challenges(request):
    try:
        user_id = request.session.get('user_id')
        challenges = SleepChallenge.objects.filter(is_active=True).order_by('-create_time')
        
        challenges_data = []
        for challenge in challenges:
            # 检查用户是否已加入该挑战
            joined = False
            completed_days = 0
            if user_id:
                user_challenge = UserChallenge.objects.filter(
                    challenge=challenge,
                    user__user_id=user_id
                ).first()
                if user_challenge:
                    joined = True
                    completed_days = user_challenge.completed_days
            
            today = timezone.now().date()
            is_expired = challenge.end_date < today
            is_checked_in_today = False
            last_checkin_date = None
            
            if joined:
                # Get last check-in date if user has joined
                last_checkin = ChallengeCheckIn.objects.filter(
                    user_challenge__user=user_id,
                    user_challenge__challenge=challenge
                ).order_by('-checkin_date').first()
                
                if last_checkin:
                    last_checkin_date = last_checkin.checkin_date.strftime('%Y-%m-%d')
                    is_checked_in_today = last_checkin.checkin_date == today
            
            challenges_data.append({
                'challenge_id': challenge.challenge_id,
                'title': challenge.challenge_title,
                'description': challenge.description,
                'start_date': challenge.start_date.strftime('%Y-%m-%d'),
                'end_date': challenge.end_date.strftime('%Y-%m-%d'),
                'initiator': challenge.initiator.user_name,
                'joined': joined,
                'completed_days': completed_days,
                'total_days': (challenge.end_date - challenge.start_date).days + 1,
                'is_expired': is_expired,
                'is_checked_in_today': is_checked_in_today,
                'last_checkin_date': last_checkin_date
            })
            
        return JsonResponse({
            'success': True,
            'challenges': challenges_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 创建挑战
@require_http_methods(["POST"])
def create_challenge(request):
    try:
        data = json.loads(request.body)
        user_id = request.session.get('user_id')
        if not user_id:
            print(f"创建挑战失败: 用户未登录, session: {request.session.items()}")
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            print(f"创建挑战失败: 用户不存在, user_id: {user_id}")
            return JsonResponse({'success': False, 'message': '用户不存在'}, status=404)
        title = data.get('title')
        description = data.get('description', '')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not all([title, start_date, end_date]):
            return JsonResponse({'success': False, 'message': '请填写完整信息'}, status=400)
            
        # 验证日期有效性
        from datetime import datetime
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            if start_date > end_date:
                return JsonResponse({'success': False, 'message': '结束日期不能早于开始日期'}, status=400)
            if start_date < timezone.now().date():
                return JsonResponse({'success': False, 'message': '开始日期不能早于今天'}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'message': '日期格式不正确，请使用YYYY-MM-DD格式'}, status=400)
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    # Get the latest challenge ID safely
                    last_challenge = SleepChallenge.objects.select_for_update().order_by('-challenge_id').first()
                    new_id = str(int(last_challenge.challenge_id) + 1).zfill(10) if last_challenge else '1000000000'
                    
                    challenge = SleepChallenge.objects.create(
                        challenge_id=new_id,
                        challenge_title=title,
                        initiator=user,
                        start_date=start_date,
                        end_date=end_date,
                        description=description
                    )
                    break
            except IntegrityError as e:
                if 'Duplicate entry' in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                raise
            
            UserChallenge.objects.create(
                user=user,
                challenge=challenge,
                completed_days=0,
                join_time=timezone.now()
            )
        
        return JsonResponse({
            'success': True,
            'message': '挑战创建成功',
            'challenge_id': challenge.challenge_id
        })
    except json.JSONDecodeError:
        print("创建挑战失败: 请求体JSON解析错误")
        return JsonResponse({'success': False, 'message': '请求数据格式错误'}, status=400)
    except Exception as e:
        print(f"创建挑战失败: {str(e)}")
        return JsonResponse({'success': False, 'message': '服务器内部错误'}, status=500)

# 加入挑战
@require_http_methods(["POST"])
def join_challenge(request, challenge_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            print(f"加入挑战失败: 用户未登录, session: {request.session.items()}")
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        try:
            user = User.objects.get(user_id=user_id)
            challenge = SleepChallenge.objects.get(challenge_id=challenge_id)
        except User.DoesNotExist:
            print(f"加入挑战失败: 用户不存在, user_id: {user_id}")
            return JsonResponse({'success': False, 'message': '用户不存在'}, status=404)
        except SleepChallenge.DoesNotExist:
            print(f"加入挑战失败: 挑战不存在, challenge_id: {challenge_id}")
            return JsonResponse({'success': False, 'message': '挑战不存在'}, status=404)
        
        # 检查是否已加入
        if UserChallenge.objects.filter(user=user, challenge=challenge).exists():
            return JsonResponse({'success': False, 'message': '您已加入该挑战'}, status=400)
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    # 再次检查是否已加入(防止并发请求)
                    if UserChallenge.objects.filter(user=user, challenge=challenge).exists():
                        return JsonResponse({'success': False, 'message': '您已加入该挑战'}, status=400)
                        
                    # 获取当前最大ID并确保类型正确
                    last_uc = UserChallenge.objects.order_by('-id').first()
                    new_id = str(int(last_uc.id) + 1) if last_uc else '1000000000'
                    
                    uc = UserChallenge.objects.create(
                        id=new_id,
                        user=user,
                        challenge=challenge,
                        completed_days=0,
                        join_time=timezone.now()
                    )
                    print(f"成功创建UserChallenge记录, id: {uc.id}")
                    
                    return JsonResponse({
                        'success': True,
                        'message': '加入挑战成功'
                    })
            except Exception as e:
                print(f"创建UserChallenge记录失败(尝试 {attempt+1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    return JsonResponse({
                        'success': False, 
                        'message': '加入挑战失败，请稍后重试'
                    }, status=500)
                time.sleep(0.5 * (attempt + 1))  # 指数退避
    except Exception as e:
        print(f"加入挑战处理异常: {str(e)}")
        return JsonResponse({'success': False, 'message': '服务器内部错误'}, status=500)

# 退出挑战
@require_http_methods(["POST"])
def leave_challenge(request, challenge_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        challenge = get_object_or_404(SleepChallenge, challenge_id=challenge_id)
        
        # 检查是否是发起者
        if challenge.initiator.user_id == user_id:
            return JsonResponse({'success': False, 'message': '发起者不能退出挑战'}, status=400)
            
        UserChallenge.objects.filter(user=user, challenge=challenge).delete()
        
        return JsonResponse({
            'success': True,
            'message': '退出挑战成功'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 打卡
@require_http_methods(["POST"])
def checkin_challenge(request, challenge_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        challenge = get_object_or_404(SleepChallenge, challenge_id=challenge_id)
        
        # 检查是否已加入
        user_challenge = UserChallenge.objects.filter(
            user=user,
            challenge=challenge
        ).first()
        if not user_challenge:
            return JsonResponse({'success': False, 'message': '您未加入该挑战'}, status=400)
            
        today = timezone.now().date()
        
        # 检查是否已打卡
        if ChallengeCheckIn.objects.filter(
            user_challenge=user_challenge,
            checkin_date=today
        ).exists():
            return JsonResponse({'success': False, 'message': '今日已打卡'}, status=400)
            
        # 验证打卡日期是否在挑战有效期内
        if today < challenge.start_date or today > challenge.end_date:
            return JsonResponse({'success': False, 'message': '当前不在挑战有效期内，无法打卡'}, status=400)
            
        # 检查是否连续打卡
        last_checkin = ChallengeCheckIn.objects.filter(
            user_challenge=user_challenge
        ).order_by('-checkin_date').first()
        
        print(f"Debug - Last checkin: {last_checkin.checkin_date if last_checkin else 'None'}, Today: {today}")
        
        if last_checkin and last_checkin.checkin_date != today:
            # 计算错过的打卡天数
            days_missed = (today - last_checkin.checkin_date).days - 1
            print(f"Debug - Days missed: {days_missed}")
            
            if days_missed > 0:
                # 生成错过的日期列表
                missed_dates = [
                    (last_checkin.checkin_date + timedelta(days=i)).strftime('%Y-%m-%d')
                    for i in range(1, days_missed + 1)
                    if (last_checkin.checkin_date + timedelta(days=i)) < today
                ]
                print(f"Debug - Missed dates: {', '.join(missed_dates)}")
                
                response = JsonResponse({
                    'success': False,
                    'message': f'请保持连续打卡，您已错过{days_missed}天打卡',
                    'details': {
                        'missed_dates': missed_dates,
                        'last_checkin_date': last_checkin.checkin_date.strftime('%Y-%m-%d'),
                        'suggestion': '请从上次打卡日期后连续打卡'
                    }
                }, status=400)
                print(f"Debug - Returning response: {response.content}")
                return response
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    # 获取当前最大ID
                    last_checkin = ChallengeCheckIn.objects.order_by('-id').first()
                    new_id = str(int(last_checkin.id) + 1) if last_checkin else '1000000000'
                    
                    # 创建打卡记录
                    checkin = ChallengeCheckIn.objects.create(
                        id=new_id,
                        user_challenge=user_challenge,
                        checkin_date=today
                    )
                    break
            except Exception as e:
                print(f"创建打卡记录失败(尝试 {attempt+1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.5 * (attempt + 1))  # 指数退避
        
        # 更新完成天数
        user_challenge.completed_days += 1
        user_challenge.save()
        
        return JsonResponse({
            'success': True,
            'message': '打卡成功',
            'completed_days': user_challenge.completed_days,
            'is_checked_in_today': True
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 获取用户参与的挑战
@require_http_methods(["GET"])
def get_user_challenges(request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        user_challenges = UserChallenge.objects.filter(user=user).select_related('challenge')
        
        challenges_data = []
        today = timezone.now().date()
        
        for uc in user_challenges:
            challenge = uc.challenge
            is_expired = challenge.end_date < today
            
            # 获取最后打卡日期
            last_checkin = ChallengeCheckIn.objects.filter(
                user_challenge=uc
            ).order_by('-checkin_date').first()
            
            # 检查今日是否已打卡
            is_checked_in_today = False
            if last_checkin and last_checkin.checkin_date == today:
                is_checked_in_today = True
            
            challenges_data.append({
                'challenge_id': challenge.challenge_id,
                'title': challenge.challenge_title,
                'start_date': challenge.start_date.strftime('%Y-%m-%d'),
                'end_date': challenge.end_date.strftime('%Y-%m-%d'),
                'completed_days': uc.completed_days,
                'total_days': (challenge.end_date - challenge.start_date).days + 1,
                'is_expired': is_expired,
                'is_checked_in_today': is_checked_in_today,
                'last_checkin_date': last_checkin.checkin_date.strftime('%Y-%m-%d') if last_checkin else None
            })
            
        return JsonResponse({
            'success': True,
            'challenges': challenges_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 获取单个挑战进度
@require_http_methods(["GET"])
def get_challenge_progress(request, challenge_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': '请先登录'}, status=401)
            
        user = get_object_or_404(User, user_id=user_id)
        challenge = get_object_or_404(SleepChallenge, challenge_id=challenge_id)
        
        # 检查是否已加入
        user_challenge = UserChallenge.objects.filter(
            user=user,
            challenge=challenge
        ).first()
        if not user_challenge:
            return JsonResponse({'success': False, 'message': '您未加入该挑战'}, status=400)
            
        # 获取打卡记录
        checkins = ChallengeCheckIn.objects.filter(
            user_challenge=user_challenge
        ).order_by('checkin_date')
        
        checkin_dates = [c.checkin_date.strftime('%Y-%m-%d') for c in checkins]
        
        return JsonResponse({
            'success': True,
            'challenge_id': challenge.challenge_id,
            'title': challenge.challenge_title,
            'completed_days': user_challenge.completed_days,
            'total_days': (challenge.end_date - challenge.start_date).days + 1,
            'checkin_dates': checkin_dates
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 自动更新挑战状态
def update_challenge_status():
    try:
        today = timezone.now().date()
        # 更新过期挑战状态
        expired_challenges = SleepChallenge.objects.filter(
            end_date__lt=today,
            is_active=True
        )
        
        count = expired_challenges.update(is_active=False)
        print(f"已更新 {count} 个过期挑战状态")
        
        return True
    except Exception as e:
        print(f"更新挑战状态失败: {str(e)}")
        return False
