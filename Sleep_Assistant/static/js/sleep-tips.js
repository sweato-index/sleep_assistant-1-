// 睡眠小贴士数据
const sleepTips = [
  { time: '06:00-12:00', tip: '早上醒来后，先喝一杯温水，有助于唤醒身体☀' },
  { time: '12:00-18:00', tip: '午饭后小憩15-30分钟，可以提高下午的工作效率💤' },
  { time: '18:00-24:00', tip: '‍晚餐后适当散步，有助于消化和放松身心🚶' },
  { time: '00:00-06:00', tip: '保持卧室黑暗安静，有助于提高睡眠质量🌙' }
];

// 获取当前时间并显示对应提示
function showSleepTip() {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes();
  const currentTime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
  
  // 找到对应时间段
  const currentTip = sleepTips.find(tip => {
    const [start, end] = tip.time.split('-');
    return currentTime >= start && currentTime < end;
  });

  // 更新卡片内容
  const tipCard = document.getElementById('sleep-tips-card');
  if (tipCard && currentTip) {
    tipCard.querySelector('.tip-content').textContent = currentTip.tip;
  }
}

// 睡眠小贴士滚动监听
function handleSleepTipsScroll() {
  console.log('Scroll handler called');
  const slider = document.querySelector('.counter_wrapper');
  const tipsContainer = document.getElementById('sleep-tips-container');
  
  if (!slider) {
    console.error('Could not find .slider-area element');
    return;
  }
  if (!tipsContainer) {
    console.error('Could not find #sleep-tips-container element');
    return;
  }

  const sliderBottom = slider.getBoundingClientRect().bottom;
  const viewportHeight = window.innerHeight;
  
  console.log('Slider bottom:', sliderBottom);
  console.log('Viewport height:', viewportHeight);

  if (sliderBottom < viewportHeight) {
    console.log('Slider bottom is above viewport - showing tips');
    tipsContainer.classList.add('visible');
  } else {
    console.log('Slider bottom is below viewport - hiding tips');
    tipsContainer.classList.remove('visible');
  }
}

// 关闭按钮功能
function setupCloseButtons() {
  const closeButtons = document.querySelectorAll('.close-btn');
  
  closeButtons.forEach(button => {
    button.addEventListener('click', () => {
      const card = button.closest('.floating-card');
      if (card) {
        card.style.display = 'none';
      }
    });
  });
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  showSleepTip();
  setupCloseButtons();
  
  // 每小时更新一次
  setInterval(showSleepTip, 60 * 60 * 1000);
  
  // 添加滚动监听
  window.addEventListener('scroll', handleSleepTipsScroll);
  
  // 初始检查，延迟100ms确保DOM完全渲染
  setTimeout(handleSleepTipsScroll, 200);
});
