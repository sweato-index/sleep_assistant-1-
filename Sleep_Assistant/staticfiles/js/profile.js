// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 个人资料相关
    initProfileForm();
    // 头像上传
    initAvatarUpload();
    // 密码修改
    initPasswordForm();
    // 提醒设置
    initReminderForm();
    // 隐私设置
    initPrivacySettings();
    // 注销账号
    initDeleteAccount();
});

// 个人资料表单处理
function initProfileForm() {
    const profileForm = document.getElementById('profileForm');
    const editBtn = document.getElementById('editProfileBtn');
    const formInputs = profileForm.querySelectorAll('input, textarea');

    // 初始状态设置为不可编辑
    formInputs.forEach(input => {
        if (input.type !== 'file') {
            input.disabled = true;
        }
    });

    // 编辑按钮点击处理
    editBtn.addEventListener('click', function() {
        const isEditing = editBtn.textContent === '保存';
        
        formInputs.forEach(input => {
            if (input.type !== 'file' && input.getAttribute('readonly') !== 'readonly') {
                input.disabled = isEditing;
            }
        });

        editBtn.textContent = isEditing ? '编辑资料' : '保存';
        editBtn.classList.toggle('btn-primary');
        editBtn.classList.toggle('btn-success');
    });

    // 个性签名字数统计
    const bioTextarea = profileForm.querySelector('textarea');
    const charCounter = profileForm.querySelector('.form-text');
    
    bioTextarea.addEventListener('input', function() {
        const remaining = this.maxLength - this.value.length;
        charCounter.textContent = `${this.value.length}/${this.maxLength}`;
    });

    // 表单提交处理
    profileForm.addEventListener('submit', function(e) {
        e.preventDefault();
        // TODO: 发送表单数据到服务器
        showToast('个人资料更新成功！');
    });
}

// 头像上传处理
function initAvatarUpload() {
    const avatarInput = document.getElementById('avatarUpload');
    const avatarImg = document.querySelector('.rounded-circle');

    avatarInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) { // 5MB限制
                showToast('图片大小不能超过5MB', 'error');
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                avatarImg.src = e.target.result;
                // TODO: 上传图片到服务器
            };
            reader.readAsDataURL(file);
        }
    });
}

// 密码修改表单处理
function initPasswordForm() {
    const passwordForm = document.getElementById('passwordForm');
    
    passwordForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const inputs = this.querySelectorAll('input[type="password"]');
        const [currentPwd, newPwd, confirmPwd] = Array.from(inputs).map(input => input.value);

        if (newPwd !== confirmPwd) {
            showToast('两次输入的新密码不一致', 'error');
            return;
        }

        // TODO: 发送密码修改请求到服务器
        showToast('密码修改成功！');
        this.reset();
    });
}

// 提醒设置表单处理
function initReminderForm() {
    const reminderForm = document.getElementById('reminderForm');
    
    reminderForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 检查是否启用了通知权限
        if (document.getElementById('browserNotification').checked) {
            Notification.requestPermission().then(function(permission) {
                if (permission === 'granted') {
                    // TODO: 保存提醒设置
                    showToast('提醒设置已更新！');
                } else {
                    showToast('请允许浏览器通知以启用提醒功能', 'warning');
                }
            });
        } else {
            // TODO: 保存提醒设置
            showToast('提醒设置已更新！');
        }
    });
}

// 隐私设置处理
function initPrivacySettings() {
    const privacyForm = document.getElementById('privacyForm');
    
    privacyForm.addEventListener('submit', function(e) {
        e.preventDefault();
        // TODO: 保存隐私设置到服务器
        showToast('隐私设置已更新！');
    });

    // 数据导出处理
    const exportBtn = document.querySelector('button[class="btn btn-primary"]');
    exportBtn.addEventListener('click', function() {
        const format = document.querySelector('select').value;
        // TODO: 处理数据导出
        showToast('数据导出已开始，请稍候...');
    });
}

// 注销账号处理
function initDeleteAccount() {
    const confirmCheckbox = document.getElementById('confirmDelete');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    
    confirmCheckbox.addEventListener('change', function() {
        confirmBtn.disabled = !this.checked;
    });

    confirmBtn.addEventListener('click', function() {
        // TODO: 发送注销请求到服务器
        showToast('账号已注销', 'error');
        setTimeout(() => {
            window.location.href = '/logout';
        }, 2000);
    });
}

// 通用提示框函数
function showToast(message, type = 'success') {
    // 如果使用 Bootstrap 的 Toast 组件
    const toastHTML = `
        <div class="toast-container position-fixed bottom-0 end-0 p-3">
            <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <strong class="me-auto">${type === 'success' ? '成功' : '提示'}</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', toastHTML);
    const toastEl = document.querySelector('.toast:last-child');
    const toast = new bootstrap.Toast(toastEl);
    toast.show();

    // 自动移除 toast
    toastEl.addEventListener('hidden.bs.toast', function() {
        this.parentElement.remove();
    });
} 