// 睡眠看板滚动监听
function handleDashboardScroll() {
  const slider = document.querySelector('.counter_wrapper');
  const dashboardContainer = document.getElementById('sleep-dashboard-container');
  
  if (!slider || !dashboardContainer) return;

  const sliderBottom = slider.getBoundingClientRect().bottom;
  const viewportHeight = window.innerHeight;

  if (sliderBottom < viewportHeight) {
    dashboardContainer.classList.add('visible');
  } else {
    dashboardContainer.classList.remove('visible');
  }
}

// 关闭睡眠看板
function closeDashboard() {
  const dashboardContainer = document.getElementById('sleep-dashboard-container');
  dashboardContainer.style.display = 'none';
}

// 初始化睡眠看板
function initSleepDashboard() {
  // 添加关闭按钮事件监听
  const closeBtn = document.querySelector('.dashboard-close-btn');
  if (closeBtn) {
    closeBtn.addEventListener('click', closeDashboard);
  }

  // 模拟最近一周的睡眠数据
  const sleepData = {
    labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    hours: [7.2, 6.8, 7.5, 7.0, 6.5, 8.0, 7.8]
  };

  // 更新昨夜睡眠时长
  const lastNightSleep = sleepData.hours[sleepData.hours.length - 1];
  document.getElementById('lastNightSleep').textContent = `${lastNightSleep}小时`;

  // 更新睡眠建议
  updateSleepAdvice(lastNightSleep);

  // 初始化图表
  initSleepChart(sleepData);

  // 添加滚动监听
  window.addEventListener('scroll', handleDashboardScroll);
  
  // 初始检查
  handleDashboardScroll();
}

// 更新睡眠建议
function updateSleepAdvice(hours) {
  const adviceElement = document.getElementById('sleepAdvice');
  let advice = '';

  if (hours >= 8) {
    advice = '您的睡眠时间充足，继续保持良好的作息习惯。';
  } else if (hours >= 7) {
    advice = '您的睡眠时间基本充足，建议适当增加睡眠时间。';
  } else {
    advice = '您的睡眠时间不足，建议调整作息，保证每天7-8小时睡眠。';
  }

  adviceElement.textContent = advice;
}

// 初始化睡眠图表
function initSleepChart(data) {
  const ctx = document.getElementById('sleepChart').getContext('2d');
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [{
        label: '睡眠时长 (小时)',
        data: data.hours,
        backgroundColor: 'rgba(255, 255, 255, 0.2)',
        borderColor: 'rgba(255, 255, 255, 0.8)',
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: '#fff',
        pointBorderColor: 'rgba(255, 255, 255, 0.8)',
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: '小时'
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: '#fff'
          }
        },
        x: {
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: '#fff'
          }
        }
      },
      plugins: {
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          bodyFont: {
            size: 14
          },
          titleFont: {
            size: 16
          }
        },
        legend: {
          display: false
        }
      }
    }
  });
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', initSleepDashboard);
