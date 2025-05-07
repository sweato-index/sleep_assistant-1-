$(document).ready(function() {
    $('#stressForm').submit(function(e) {
        e.preventDefault();
        
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
            bmiCategory === 'normal_weight' ? 1 : 0,
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
                const result = response.result;
                $('#stressResult').text(result);
                $('#resultContainer').show();
                
                // 根据结果添加样式
                if (result >= 7) {
                    $('#stressResult').css('color', 'red');
                } else if (result >= 4) {
                    $('#stressResult').css('color', 'orange');
                } else {
                    $('#stressResult').css('color', 'green');
                }
            },
            error: function(xhr, status, error) {
                console.error(error);
                alert('评估失败，请稍后再试');
            }
        });
    });
});
