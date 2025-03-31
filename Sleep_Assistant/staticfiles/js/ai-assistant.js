// AI助手悬浮球交互
document.addEventListener('DOMContentLoaded', function() {
  const floatBtn = document.querySelector('.ai-assistant-float');
  
  if (floatBtn) {
    floatBtn.addEventListener('click', function() {
      window.location.href = "/ai-assistant/";
    });
    
    // 添加悬浮球显示动画
    setTimeout(() => {
      floatBtn.style.opacity = '1';
      floatBtn.style.transform = 'translateY(0)';
    }, 1000);
  }
});
