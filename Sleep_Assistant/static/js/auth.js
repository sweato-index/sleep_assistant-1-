/**
 * 全局认证状态管理
 */

// 全局认证状态
let authState = {
    isAuthenticated: false,
    user: null
};

// 初始化认证状态
function initAuth() {
    // 从localStorage恢复状态
    const savedAuth = localStorage.getItem('authState');
    if (savedAuth) {
        authState = JSON.parse(savedAuth);
    }
    
    // 检查服务器端session
    checkSession();
    
    // 更新UI
    updateAuthUI();
}

// 检查服务器端session状态
function checkSession() {
    $.ajax({
        url: '/api/login/check',
        method: 'GET',
        success: function(response) {
            if (response.isAuthenticated) {
                authState.isAuthenticated = true;
                authState.user = response.user;
                saveAuthState();
                updateAuthUI();
            } else {
                clearAuthState();
            }
        },
        error: function() {
            console.error('Session check failed');
        }
    });
}

// 登录成功处理
function handleLoginSuccess(userData) {
    authState.isAuthenticated = true;
    authState.user = userData;
    saveAuthState();
    updateAuthUI();
    
    // 根据用户类型跳转不同页面
    const userType = String(userData.user_type); // 确保user_type是字符串
    if (userType === '0') {
        // 管理员跳转到管理后台
        window.location.href = '/api/admin/dashboard/';
    } else {
        // 普通用户跳转到首页
        window.location.href = '/';
    }
}

// 登出处理
function handleLogout() {
    $.ajax({
        url: '/api/logout/',
        method: 'POST',
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function() {
            clearAuthState();
            location.reload();
        },
        error: function() {
            console.error('Logout failed');
        }
    });
}

// 保存认证状态到localStorage
function saveAuthState() {
    localStorage.setItem('authState', JSON.stringify(authState));
}

// 清除认证状态
function clearAuthState() {
    authState.isAuthenticated = false;
    authState.user = null;
    localStorage.removeItem('authState');
    updateAuthUI();
}

// 更新UI显示登录状态
function updateAuthUI() {
    const $userAvatar = $('.user-avatar img');
    const $dropdownMenu = $('.header-user-profile .dropdown-menu');
    
    if (authState.isAuthenticated && authState.user) {
        // 已登录状态
        const avatarUrl = authState.user.avatar_url 
            ? '/media/' + authState.user.avatar_url 
            : '/static/img/author-1.png';
        $userAvatar.attr('src', avatarUrl);
        
        $dropdownMenu.empty();
        $dropdownMenu.append(`
            <li><a href="/profile/">个人中心</a></li>
            <li><a href="#" id="logoutBtn">退出登录</a></li>
        `);
        
        // 绑定登出事件
        $(document).off('click', '#logoutBtn').on('click', '#logoutBtn', function(e) {
            e.preventDefault();
            handleLogout();
        });
    } else {
        // 未登录状态
        $userAvatar.attr('src', '/static/img/author-1.png');
        
        $dropdownMenu.empty();
        $dropdownMenu.append(`
            <li><a href="#signinModal" data-bs-toggle="modal">登录</a></li>
            <li><a href="#signupModal" data-bs-toggle="modal">注册</a></li>
        `);
    }
}

// 页面加载时初始化
$(document).ready(function() {
    initAuth();
});

// 全局访问
window.auth = {
    getState: () => authState,
    login: handleLoginSuccess,
    logout: handleLogout,
    checkSession: checkSession
};
