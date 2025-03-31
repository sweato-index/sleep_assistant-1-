// assets/js/sleep-assessment.js

const SleepAssessment = (() => {
    // 私有变量
    let sleepRadarChart;
    const MAX_SCORE = 19;
    const DIMENSION_MAP = {
        q1: '入睡潜伏期',
        q2: '睡眠时长',
        q4: '睡眠效率',
        q6: '日间功能',
        q7: '呼吸症状',
        q8: '肢体症状'
    };

    // 初始化雷达图
    const initCharts = () => {
        const ctx = document.getElementById('sleepRadarChart')?.getContext('2d');
        if (!ctx) return;

        sleepRadarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.values(DIMENSION_MAP),
                datasets: [{
                    label: '睡眠维度分析',
                    data: new Array(6).fill(0),
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)'
                }]
            },
            options: {
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 3,
                        ticks: {
                            stepSize: 1,
                            showLabelBackdrop: false
                        }
                    }
                }
            }
        });
    };

    // 验证表单
    const validateForm = (formData) => {
        const requiredQuestions = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6'];
        return requiredQuestions.filter(q => !formData.has(q));
    };

    // 计算各维度得分
    const calculateScores = (formData) => ({
        q1: 4-parseInt(formData.get('q1')) || 0,
        q2: 3-parseInt(formData.get('q2')) || 0,
        q3: 3-parseInt(formData.get('q3')) || 0,
        q4: 2-parseInt(formData.get('q4')) || 0,
        q5: 2-parseInt(formData.get('q5')) || 0,
        q6: 2-parseInt(formData.get('q6')) || 0,
        q7: 2-Array.from(formData.getAll('q7')).reduce((a, v) => a + parseInt(v), 0),
        q8: 2-Array.from(formData.getAll('q8')).reduce((a, v) => a + parseInt(v), 0),
        
    });

    // 更新进度条
    const updateProgress = (score) => {
        const progress = document.getElementById('sleep-progress');
        if (!progress) return;

        const percentage = (score / MAX_SCORE) * 100;
        progress.style.width = `${percentage}%`;
        progress.textContent = `${score}/${MAX_SCORE}`;
        progress.className = `progress-bar progress-bar-striped ${
            score >= 14 ? 'bg-success' :      // 15-19 优秀
            score >= 9 ? 'bg-primary' :       // 10-14 良好
            score >= 5 ? 'bg-warning' :         // 5-9 一般
            'bg-danger'                        // 0-4 需关注
        }`;
        
        document.getElementById('sleep-score').textContent = score;
    };

    // 更新维度分数显示
    const updateDimensions = (scores) => {
        Object.entries(scores).forEach(([q, score]) => {
            const element = document.getElementById(`dimension-${q}`);
            if (element) {
                element.textContent = score;
                
                // 根据各维度最大值设置颜色梯度
                // 假设各维度最高分：
                // q1:3, q2:3, q3:3, q4:2, q5:2, q6:2, q7:2, q8:2
                const maxScoreMap = {
                    q1: 3,
                    q2: 3,
                    q3: 3,
                    q4: 2,
                    q5: 2,
                    q6: 2,
                    q7: 2,
                    q8: 2
                };
                
                const threshold = maxScoreMap[q] * 0.7; // 按最高分的70%作为优良分界线
                element.className = `badge rounded-pill ${
                    score >= threshold ? 'bg-success' :       // 前30%优秀
                    score >= (threshold * 0.5) ? 'bg-primary' : // 中间35%良好
                    'bg-danger'                                // 后35%需关注
                }`;
            }
        });
    };

    // 更新雷达图数据
    const updateRadarChart = (scores) => {
        if (!sleepRadarChart) return;
        
        sleepRadarChart.data.datasets[0].data = [
            scores.q1, scores.q2, scores.q4,
            scores.q6, scores.q7, scores.q8
        ];
        sleepRadarChart.update();
    };

    const showRecommendations = (score) => {
        const recommendations = [
            { threshold: 18, 
              text: "您的睡眠质量非常优秀",
              detail: "继续保持：\n• 规律作息\n• 健康饮食\n• 适度运动" },
            { threshold: 13,
              text: "您的睡眠质量良好",
              detail: "改进建议：\n• 减少睡前使用电子设备\n• 保持卧室安静舒适" },
            { threshold: 10,
              text: "您的睡眠质量一般",
              detail: "需要关注：\n• 记录睡眠日记\n• 调整作息时间" },
            { threshold: 0,
              text: "您的睡眠质量较差",
              detail: "立即行动：\n• 咨询专业医师\n• 进行睡眠监测" }
        ];
    
        // 清理旧提示框
        const oldAlert = document.getElementById('resultAlert');
        if (oldAlert) oldAlert.remove();
    
        // 创建新提示框
        const alertHTML = `
            <div class="alert alert-info mt-4 alert-dismissible fade show" id="resultAlert">
                <h5 class="alert-heading" id="resultText"></h5>
                
            </div>
        `;
        
        // 插入到结果卡片内部（重要修改点）
        document.querySelector('.assessment-result .card-body').insertAdjacentHTML('beforeend', alertHTML);
        
        // 获取结果对象
        const result = recommendations.find(r => score <= r.threshold) || recommendations[3];
        
        // 立即填充内容（确保元素存在）
        const alertBox = document.getElementById('resultAlert');
        alertBox.querySelector('#resultText').innerHTML = `
            <strong>${result.text}</strong><br>
            <small class="text-muted">${result.detail.replace(/\n/g, '<br>')}</small>
        `;
    
        // 初始化Bootstrap组件（重要新增）
        new bootstrap.Alert(alertBox);
        alertBox.scrollIntoView({ behavior: 'smooth' });
    };
    
    // 移除原有的createResultAlert函数

    // 表单提交处理
    const handleFormSubmit = (e) => {
        
        
        e.preventDefault();
        
    
        const formData = new FormData(e.target);
        
        
        // 验证必填项
        const missingQuestions = validateForm(formData);
        if (missingQuestions.length > 0) {
            alert(`请完成以下问题：${missingQuestions.map(q => `第${q.slice(1)}题`).join(', ')}`);
            return;
        }

        // 计算得分
        const scores = calculateScores(formData);
        const totalScore = Object.values(scores).reduce((a, b) => a + b, 0);

        // 更新界面
        updateProgress(totalScore);
        updateDimensions(scores);
        updateRadarChart(scores);
        showRecommendations(totalScore);
    };

    // 暴露的公共方法
    return {
        init: () => {
            initCharts();
            document.getElementById('sleepAssessmentForm')?.addEventListener('submit', handleFormSubmit);
        }
    };
})();

// 初始化模块
document.addEventListener('DOMContentLoaded', () => {
    SleepAssessment.init();
});