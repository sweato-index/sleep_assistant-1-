from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from .models import SleepRecord  # 注意导入路径
from django.shortcuts import (
    render, 
    redirect, 
    get_object_or_404, 
    get_list_or_404
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.utils.decorators import method_decorator
from utils.decorators import session_login_required

@method_decorator(session_login_required, name='dispatch')
class SleepRecordAPI(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            return JsonResponse({'status': 'error', 'message': '未登录'}, status=401)
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            print("✅ POST 请求收到")
            print("request.POST =", request.POST)


            from datetime import datetime, time, timedelta
            
            user_id = request.session.get('user_id')
            sleep_time_str = request.POST.get('sleep_time')
            wake_time_str = request.POST.get('wake_time')
            sleep_hours = request.POST.get('sleep_hours')
            rating = request.POST.get('sleepQuality')

            if not sleep_time_str:
                return JsonResponse({'status': 'error', 'message': 'sleep_time is required'}, status=400)

            try:
                # 处理sleep_time
                if 'T' in sleep_time_str:
                    naive_sleep_time = datetime.strptime(sleep_time_str, '%Y-%m-%dT%H:%M')
                else:
                    naive_sleep_time = datetime.combine(
                        datetime.strptime(sleep_time_str, '%Y-%m-%d').date(),
                        time(23, 0))  # 默认晚上11点入睡
                
                sleep_time = timezone.make_aware(naive_sleep_time)
                
                # 处理wake_time (可选)
                wake_time = None
                if wake_time_str:
                    if 'T' in wake_time_str:
                        naive_wake_time = datetime.strptime(wake_time_str, '%Y-%m-%dT%H:%M')
                    else:
                        naive_wake_time = datetime.combine(
                            datetime.strptime(wake_time_str, '%Y-%m-%d').date(),
                            time(7, 0))  # 默认早上7点醒来
                    
                    wake_time = timezone.make_aware(naive_wake_time)
                    
                    # 确保醒来时间在入睡时间之后
                    if wake_time <= sleep_time:
                        wake_time = wake_time + timedelta(days=1)
                    
                    # 如果提供了wake_time，计算sleep_hours
                    sleep_hours = (wake_time - sleep_time).total_seconds() / 3600
                elif not sleep_hours:
                    return JsonResponse({'status': 'error', 'message': 'Either wake_time or sleep_hours is required'}, status=400)

            except ValueError as e:
                return JsonResponse({'status': 'error', 'message': f'时间格式错误: {str(e)}'}, status=400)

            data = {
                'record_id': self.generate_record_id(),
                'user_id': user_id,
                'record_time': timezone.now(),
                'sleep_time': sleep_time,
                'wake_time': wake_time if wake_time else None,
                'sleep_hours': sleep_hours,
                'rating': rating
            }
            SleepRecord.objects.create(**data)
            return JsonResponse({'status': 'success', 'message': '记录保存成功'})
        except Exception as e:
            print('保存异常:', e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def get(self, request):
        records = SleepRecord.objects.filter(user=request.user)
        return JsonResponse({'data': list(records.values())})

    def delete(self, request, record_id):
        record = get_object_or_404(SleepRecord, record_id=record_id)
        record.delete()
        return JsonResponse({'status': 'success'})

    def generate_record_id(self):
        return f"REC{int(timezone.now().timestamp())}"
