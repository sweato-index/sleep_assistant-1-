from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import joblib
import numpy as np
import os
import json
from django.conf import settings

def render_stress_assessment(request):
    return render(request, 'stress-assessment.html')

@csrf_exempt
def predict_stress(request):
    if request.method == 'POST':
        try:
            # 调试日志
            print("Received prediction request")
            
            # 加载模型和标准化器
            model_path = os.path.join(settings.BASE_DIR, 'static', 'model', 'xgb_model.pkl')
            scaler_path = os.path.join(settings.BASE_DIR, 'static', 'model', 'scaler.pkl')
            
            print(f"Model path: {model_path}")
            print(f"Scaler path: {scaler_path}")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}")
            if not os.path.exists(scaler_path):
                raise FileNotFoundError(f"Scaler file not found at {scaler_path}")
            
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            
            # 获取前端数据
            data = json.loads(request.body).get('data')
            if not data or len(data) != 24:
                return JsonResponse({'error': 'Invalid input data'}, status=400)
            
            print(f"Input data: {data}")
            
            # 转换为numpy数组并标准化
            input_data = np.array(data).reshape(1, -1)
            scaled_data = scaler.transform(input_data)
            
            # 进行预测
            prediction = model.predict(scaled_data)
            result = int(np.round(prediction[0]))
            
            print(f"Prediction result: {result}")
            
            return JsonResponse({'result': result})
            
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
