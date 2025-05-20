(() => {




    document.getElementById('quickRecordForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData();
    const recordDate = document.getElementById('recordDate').value;
    const sleepHours = document.getElementById('sleepHours').value;
    const sleepQuality = document.getElementById('sleepQuality').value;

    formData.append('record_date', recordDate);
    formData.append('sleep_hours', sleepHours);
    formData.append('sleepQuality', sleepQuality);

    fetch('/api/sleep-record/', {
        method: 'POST',
        headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        },
        body: formData,
        credentials: 'include'  // 发送 sessionid 保证登录状态
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('submitStatus').textContent =
            data.message || (data.status === 'success' ? '保存成功' : '保存失败');
    })
    .catch(() => {
        document.getElementById('submitStatus').textContent = '请求出错，请稍后重试';
    });
    });

    // 私有变量
    let sleepData = {};
    let calendar, durationChart, qualityChart;
    const API_ENDPOINT = '/api/sleep-records/';
    let dailyChart = null;

    // 初始化函数
    const init = () => {
        loadLocalData();
        initCalendar();
        initCharts();
        
        initTooltips();
    };

    // 加载本地数据
    const loadLocalData = () => {
        const storedData = localStorage.getItem('sleepData');
        sleepData = storedData ? JSON.parse(storedData) : {
            "2023-10-01": { quality: 5, hours: 8.2 },
            "2023-10-02": { quality: 4, hours: 7.5 },
            "2023-10-03": { quality: 3, hours: 6.8 },
            "2023-10-04": { quality: 2, hours: 5.5 },
            "2023-10-05": { quality: 1, hours: 4.1 }
        };
    };

    // 初始化日历
    const initCalendar = async () => {
        const calendarEl = document.getElementById('calendar');
        
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'zh-cn',
            events: async (fetchInfo, successCallback) => {
                try {
                    const response = await fetch(`${API_ENDPOINT}?start=${fetchInfo.startStr}&end=${fetchInfo.endStr}`);
                    const records = await response.json();
                    successCallback(records.map(transformEventData));
                } catch (error) {
                    console.error('日历数据加载失败:', error);
                }
            },
            eventDidMount: handleEventMount,
            eventClick: handleEventClick
        });
        
        calendar.render();
    };


    const transformEventData = (record) => ({
        id: record.record_id,
        title: `${getQualityIcon(record.rating)} ${record.duration}h`,
        start: record.sleep_time,
        end: record.wake_time,
        extendedProps: {
            sleep_time: formatTime(record.sleep_time),
            wake_time: formatTime(record.wake_time),
            duration: record.duration,
            stages: record.stages  // 假设后端返回睡眠阶段数据
        }
    });

    



    // 新增事件点击处理函数
    const handleEventClick = async (info) => {
        try {
            const response = await fetch(`${API_ENDPOINT}${info.event.id}/`);
            const detailData = await response.json();

            // 填充基础数据
            document.getElementById('detailDate').textContent = 
                new Date(detailData.sleep_time).toLocaleDateString();
            document.getElementById('detailSleepTime').textContent = 
                formatTime(detailData.sleep_time);
            document.getElementById('detailWakeTime').textContent = 
                formatTime(detailData.wake_time);
            document.getElementById('detailDuration').textContent = 
                `${detailData.duration}小时`;
            document.getElementById('detailRating').textContent = 
                getQualityLabel(detailData.rating);

            // 生成图表
            renderDailyChart(detailData.stages);
            new bootstrap.Modal('#detailModal').show();
        } catch (error) {
            showToast('详情加载失败', 'error');
        }
    };

    const formatTime = (isoString) => 
        new Date(isoString).toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });



    // 生成日历事件
    
    const generateCalendarEvents = () => {
        return Object.entries(sleepData).map(([date, data]) => ({
            start: date,
            title: `${getQualityIcon(data.quality)} ${data.hours}h`,
            className: [`${getQualityClass(data.quality)}`],
            extendedProps: {
                hours: data.hours,
                quality: data.quality,
                // 可添加更多详细数据
                stages: {  // 示例睡眠阶段数据
                    deep: data.hours * 0.6,
                    light: data.hours * 0.3,
                    awake: 24 - data.hours
                }
            }
        }));
    };
    const getQualityIcon = quality => 
        ['😞', '😕', '😐', '😊', '😄'][quality - 1];
    
    const renderDailyChart = (stages) => {
        const ctx = document.getElementById('dailyChart');
        
        if (dailyChart) dailyChart.destroy();
        
        dailyChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['深度睡眠', '浅度睡眠', '快速眼动', '清醒时间'],
                datasets: [{
                    data: Object.values(stages),
                    backgroundColor: ['#4CAF50', '#FFC107', '#2196F3', '#F44336']
                }]
            },
            options: {
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (ctx) => 
                                `${ctx.label}: ${ctx.raw.toFixed(1)}小时`
                        }
                    }
                }
            }
        });
    };
    
    const getQualityLabel = (rating) => 
        ['极差', '较差', '一般', '良好', '优秀'][rating - 1];


    // 睡眠质量分类
    const getQualityClass = quality => {
        const qualityMap = {
            5: 'excellent',  // 优秀
            4: 'good',       // 良好
            3: 'average',    // 一般
            2: 'poor',       // 较差
            1: 'critical'    // 极差
        };
        return `fc-event-${qualityMap[quality]}`;
    };

    // 事件挂载处理
    const handleEventMount = info => {
        info.el.setAttribute('data-bs-toggle', 'tooltip');
        info.el.setAttribute('title', `${info.event.extendedProps.hours}小时`);
    };

    // 日期点击处理
    const handleDateClick = info => {
        // 填充日期输入框
        const dateInput = document.getElementById('recordDate');
        dateInput.value = info.dateStr;
        
        // 添加日期输入框动画
        dateInput.animate([
            { transform: 'scale(1)' },
            { transform: 'scale(1.05)' },
            { transform: 'scale(1)' }
        ], {
            duration: 200,
            easing: 'ease-out'
        });

        // 添加日历单元格动画
        info.dayEl.animate([
            { transform: 'scale(1)', backgroundColor: 'transparent' },
            { transform: 'scale(1.1)', backgroundColor: '#c0b4f8a1' },
            { transform: 'scale(1)', backgroundColor: 'transparent' }
        ], {
            duration: 300,
            easing: 'ease-out'
        });

        // 添加波纹效果
        const ripple = document.createElement('div');
        ripple.className = 'ripple-effect';
        info.dayEl.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);

        // 移除之前的高亮
        const prevHighlighted = document.querySelector('.fc-day-highlight');
        if (prevHighlighted) {
            prevHighlighted.classList.remove('fc-day-highlight');
        }
        
        // 添加新的高亮
        info.dayEl.classList.add('fc-day-highlight');
    };

    // 初始化图表
    const initCharts = () => {
        durationChart = createDurationChart();
        qualityChart = createQualityChart();
    };

    // 创建时长图表
    const createDurationChart = () => new Chart(document.getElementById('durationChart'), {
        type: 'line',
        data: getDurationChartData(),
        options: getChartOptions()
    });

    // 创建质量图表
    const createQualityChart = () => new Chart(document.getElementById('qualityChart'), {
        type: 'bar',
        data: getQualityChartData(),
        options: getChartOptions()
    });

    // 获取图表通用配置
    const getChartOptions = () => ({
        responsive: true,
        plugins: { legend: { display: false } }
    });

    // 获取时长图表数据
    const getDurationChartData = () => ({
        labels: Object.keys(sleepData),
        datasets: [{
            label: '睡眠时长（小时）',
            data: Object.values(sleepData).map(d => d.hours),
            borderColor: '#2196F3',
            tension: 0.4,
            fill: false
        }]
    });

    // 获取质量图表数据
    const getQualityChartData = () => ({
        labels: ['优秀', '良好', '一般', '较差', '极差'], // 5个标签
        datasets: [{
            label: '天数',
            data: calculateQualityDistribution(),
            backgroundColor: [
                '#00C853', // 优秀
                '#64DD17', // 良好
                '#FFD600', // 一般
                '#FF6D00', // 较差
                '#D50000'  // 极差
            ]
        }]
    });

    // 计算质量分布
    const calculateQualityDistribution = () => {
        const counts = new Array(5).fill(0); // 5个分类
        Object.values(sleepData).forEach(d => {
            if(d.quality >=1 && d.quality <=5) counts[d.quality-1]++
        });
        return counts;
    };
    const recommendations = [
        {
            threshold: 90,
            text: "睡眠质量极佳",
            detail: "保持建议：\n• 维持当前作息规律\n• 每周保持5次以上运动\n• 注意压力管理"
        },
        {
            threshold: 75,
            text: "睡眠质量良好",
            detail: "优化建议：\n• 避免睡前使用电子设备\n• 保持卧室温度18-22℃"
        },
        {
            threshold: 60,
            text: "睡眠质量一般",
            detail: "改善建议：\n• 建立固定作息时间\n• 限制咖啡因摄入"
        },
        {
            threshold: 40,
            text: "睡眠质量较差",
            detail: "预警建议：\n• 进行睡眠日记记录\n• 咨询家庭医生"
        },
        {
            threshold: 0,
            text: "睡眠质量极差",
            detail: "立即行动：\n• 进行专业睡眠检测\n• 排除睡眠呼吸暂停"
        }
    ];
    const getQualityAdvice = quality => [
        "您的睡眠质量已达到最佳状态，继续保持！",
        "睡眠状况良好，仍有小幅优化空间",
        "睡眠质量处于平均水平，建议关注改善",
        "睡眠质量低于正常水平，需要引起重视",
        "睡眠状况严重异常，建议立即就医检查"
    ][quality - 1];
    // 绑定事件
    const bindEvents = () => {
        
    };

    // 表单提交处理
    const handleFormSubmit = e => {
        e.preventDefault();
        const newRecord = getFormData();
        
        // 更新数据
        updateData(newRecord);
        saveData();
        
        // 获取最新事件数据
        const newEvent = generateCalendarEvents()
            .find(event => event.start === newRecord.date);
    
        // 移除旧事件（如果存在）
        const existingEvents = calendar.getEvents();
        const oldEvent = existingEvents.find(e => e.startStr === newRecord.date);
        if (oldEvent) oldEvent.remove();
    
        // 添加新事件
        if (newEvent) calendar.addEvent(newEvent);
    
        // 强制重渲染
        calendar.updateSize();
        calendar.render();
    
        // 更新其他可视化组件
        updateVisualizations();
        resetForm(e.target);
    };

    // 获取表单数据
    const getFormData = () => ({
        date: document.getElementById('recordDate').value,
        hours: parseFloat(document.getElementById('sleepHours').value),
        quality: parseInt(document.getElementById('sleepQuality').value)
    });

    // 更新数据
    const updateData = newRecord => {
        sleepData[newRecord.date] = {
            hours: newRecord.hours, 
            quality: newRecord.quality
        };
    };

    // 更新可视化
    const updateVisualizations = () => {
        durationChart.data = getDurationChartData();
        qualityChart.data = getQualityChartData();
        durationChart.update();
        qualityChart.update();
        calendar.refetchEvents();
    };

    // 保存数据
    const saveData = () => 
        localStorage.setItem('sleepData', JSON.stringify(sleepData));

    // 重置表单
    const resetForm = form => form.reset();

    // 初始化工具提示
    const initTooltips = () => 
        $('[data-bs-toggle="tooltip"]').tooltip();

    // 启动应用
    if (document.readyState !== 'loading') {
        init();
    } else {
        document.addEventListener('DOMContentLoaded', init);
    }
})();
