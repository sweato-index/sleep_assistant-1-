$(document).ready(function() {
    // 全局点击事件监听
    $(document).on('click', function(e) {
        console.log('Document click detected on:', e.target);
        
        // 处理模态框按钮点击
        const $modalBtn = $(e.target).closest('[data-bs-toggle="modal"]');
        if ($modalBtn.length) {
            console.group('Modal button click debug');
            console.log('Modal button found:', $modalBtn[0]);
            console.log('Button href:', $modalBtn.attr('href'));
            
            e.preventDefault();
            const target = $modalBtn.attr('href');
            console.log('Modal target:', target);
            
            // 检查元素是否可见
            console.log('Element visible:', $modalBtn.is(':visible'));
            console.log('Element data:', $modalBtn.data());
            
            // 确保模态框元素存在
            if ($(target).length) {
                console.log('Showing modal:', target);
                $(target).modal('show');
            } else {
                console.error('Modal element not found:', target);
            }
            
            console.groupEnd();
            return false;
        }
    });

    // 初始化模态框
    $('#signinModal').modal({
        show: false,
        backdrop: 'static'
    });
    $('#signupModal').modal({
        show: false,
        backdrop: 'static'
    });

    // 登录表单验证
    $('#loginForm').submit(function(e) {
        e.preventDefault();
        
        const phone = $('#loginPhone').val().trim();
        const password = $('#loginPassword').val().trim();
        
        if (!phone) {
            showAlert('请输入手机号', 'danger');
            return;
        }
        
        if (!password) {
            showAlert('请输入密码', 'danger');
            return;
        }
        
        // 真实登录请求
        loginUser(phone, password);
    });

    // 注册表单验证
    $('#registerForm').submit(function(e) {
        e.preventDefault();
        
        const name = $('#registerName').val().trim();
        const phone = $('#registerPhone').val().trim();
        const email = $('#registerEmail').val().trim();
        const password = $('#registerPassword').val();
        const confirmPassword = $('#confirmPassword').val();
        const code = $('#verificationCode').val().trim();
        
        if (!name) {
            showAlert('请输入用户名', 'danger');
            return;
        }
        
        if (!phone) {
            showAlert('请输入手机号', 'danger');
            return;
        }
        
        if (!/^1[3-9]\d{9}$/.test(phone)) {
            showAlert('请输入正确的手机号', 'danger');
            return;
        }

        if (!email) {
            showAlert('请输入邮箱', 'danger');
            return;
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            showAlert('请输入有效的邮箱地址', 'danger');
            return;
        }
        
        if (password.length < 6 || password.length > 20) {
            showAlert('密码长度应为6-20位', 'danger');
            return;
        }
        
        if (password !== confirmPassword) {
            showAlert('两次输入的密码不一致', 'danger');
            return;
        }
        
        if (!code) {
            showAlert('请输入验证码', 'danger');
            return;
        }
        
        if (!$('#agreeTerms').is(':checked')) {
            showAlert('请同意用户协议', 'danger');
            return;
        }
        
        // 发送注册请求
        $.ajax({
            url: '/api/register/',
            method: 'POST',
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            data: {
                name: name,
                phone: phone,
                email: email,
                password: password
            },
            success: function(response) {
                if (response.success) {
                    showAlert('注册成功', 'success');
                    $('#signupModal').modal('hide');
                } else {
                    showAlert(response.message, 'danger');
                }
            },
            error: function(xhr) {
                showAlert('注册失败: ' + xhr.responseJSON?.message || '服务器错误', 'danger');
            }
        });
    });

    // 获取验证码
    $('#getCodeBtn').click(function() {
        const phone = $('#registerPhone').val().trim();
        
        if (!phone) {
            showAlert('请输入手机号', 'danger');
            return;
        }
        
        if (!/^1[3-9]\d{9}$/.test(phone)) {
            showAlert('请输入正确的手机号', 'danger');
            return;
        }
        
        // 禁用按钮并开始倒计时
        const $btn = $(this);
        let countdown = 60;
        
        $btn.prop('disabled', true);
        $btn.text(`${countdown}秒后重新获取`);
        
        const timer = setInterval(() => {
            countdown--;
            $btn.text(`${countdown}秒后重新获取`);
            
            if (countdown <= 0) {
                clearInterval(timer);
                $btn.prop('disabled', false);
                $btn.text('获取验证码');
            }
        }, 1000);
        
        // 模拟发送验证码
        simulateSendCode(phone);
    });

    // 显示提示信息
    function showAlert(message, type) {
        const $alert = $(`<div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>`);
        
        $('.modal-body').prepend($alert);
        
        setTimeout(() => {
            $alert.alert('close');
        }, 3000);
    }

// 真实登录请求
function loginUser(phone, password) {
    showAlert('登录请求发送中...', 'info');
    
    $.ajax({
        url: '/api/login/',
        method: 'POST',
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        data: {
            phone: phone,
            password: password
        },
        success: function(response) {
            if (response.success) {
                showAlert('登录成功', 'success');
                $('#signinModal').modal('hide');
                auth.login(response.user);
            } else {
                showAlert(response.message, 'danger');
            }
        },
        error: function(xhr) {
            showAlert('登录失败: ' + (xhr.responseJSON?.message || '服务器错误'), 'danger');
        }
    });
}
});
