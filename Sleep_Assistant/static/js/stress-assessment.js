$(document).ready(function() {
    // 压力等级建议
    const stressAdvice = {
        1: "您的压力水平非常低，继续保持健康的生活方式即可。",
        2: "压力水平较低，注意保持工作和生活的平衡。",
        3: "压力水平适中，建议每天进行15分钟的冥想放松。", 
        4: "压力水平略高，尝试增加运动量和改善睡眠质量。",
        5: "压力水平中等偏高，建议减少咖啡因摄入并增加休息时间。",
        6: "压力水平较高，考虑进行深呼吸练习或寻求社交支持。",
        7: "压力水平很高，建议咨询专业人士并调整工作节奏。",
        8: "压力水平非常高，需要立即采取措施减压并寻求帮助。",
        9: "压力水平极高，建议就医并制定全面的减压计划。",
        10: "压力水平危险，请立即寻求专业医疗和心理帮助。"
    };

    $('#stressForm').submit(function(e) {
        e.preventDefault();
        
        // 显示加载状态
        const submitBtn = $(this).find('button[type="submit"]');
        submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>评估中...');

        // 收集数值型数据
        const age = parseInt($('#age').val());
        const sleepDuration = parseFloat($('#sleepDuration').val());
        const activityLevel = parseInt($('#activityLevel').val());
        const heartRate = parseInt($('#heartRate').val());
        const dailySteps = parseInt($('#dailySteps').val());

        // 处理分类变量
        const gender = $('#gender').val();
        const occupation = $('#occupation').val();
        const bmiCategory = $('#bmiCategory').val();
        const sleepDisorder = $('#sleepDisorder').val();

        // 构建模型需要的数组
        const inputData = [
            age,
            sleepDuration,
            activityLevel,
            heartRate,
            dailySteps,
            // 性别编码
            gender === 'female' ? 1 : 0,
            gender === 'male' ? 1 : 0,
            // 职业编码
            occupation === 'accountant' ? 1 : 0,
            occupation === 'doctor' ? 1 : 0,
            occupation === 'engineer' ? 1 : 0,
            occupation === 'lawyer' ? 1 : 0,
            occupation === 'manager' ? 1 : 0,
            occupation === 'nurse' ? 1 : 0,
            occupation === 'sales_rep' ? 1 : 0,
            occupation === 'salesperson' ? 1 : 0,
            occupation === 'scientist' ? 1 : 0,
            occupation === 'software_engineer' ? 1 : 0,
            occupation === 'teacher' ? 1 : 0,
            // BMI分类编码
            bmiCategory === 'normal' ? 1 : 0,
            bmiCategory === 'overweight' ? 1 : 0,
            bmiCategory === 'obese' ? 1 : 0,
            // 睡眠障碍编码
            sleepDisorder === 'insomnia' ? 1 : 0,
            sleepDisorder === 'sleep_apnea' ? 1 : 0
        ];

        // 发送数据到后端
        $.ajax({
            url: '/api/predict-stress/',
            type: 'POST',
            data: JSON.stringify({data: inputData}),
            contentType: 'application/json',
            success: function(response) {
                const result = Math.round(response.result); // 四舍五入到整数
                
                // 显示结果
                $('#stressResult').text(result);
                $('#resultContainer').fadeIn(500);
                
                // 设置压力计位置 (0-100%)
                const meterPosition = (result - 1) * (100 / 9);
                $('#stressIndicator').css('left', meterPosition + '%');
                
                // 根据结果添加样式和建议
                let resultColor, resultClass;
                if (result >= 8) {
                    resultColor = '#dc3545';
                    resultClass = 'text-danger';
                } else if (result >= 5) {
                    resultColor = '#fd7e14';
                    resultClass = 'text-warning';
                } else {
                    resultColor = '#28a745';
                    resultClass = 'text-success';
                }
                
                $('#stressResult').removeClass('text-danger text-warning text-success')
                                 .addClass(resultClass);
                
                // 显示建议
                $('#stressAdvice').html(stressAdvice[result]);
                $('#adviceContainer').fadeIn(800);
                
                // 滚动到结果区域
                $('html, body').animate({
                    scrollTop: $('#resultContainer').offset().top - 100
                }, 500);
            },
            error: function(xhr, status, error) {
                console.error(error);
                alert('评估失败，请检查输入数据后重试');
            },
            complete: function() {
                submitBtn.prop('disabled', false).html('<i class="fas fa-chart-line me-2"></i>评估压力水平');
            }
        });
    });
});
