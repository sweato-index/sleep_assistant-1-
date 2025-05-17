$(document).ready(function() {
    // 检查管理员登录状态
    checkAdminStatus();
    
    // 绑定导航链接点击事件
    $('#dashboard-link').click(function(e) {
        e.preventDefault();
        loadDashboard();
    });
    
    $('#users-link').click(function(e) {
        e.preventDefault();
        loadUsers();
    });
    
    $('#logout-btn').click(function() {
        logout();
    });

    $('#content-link').click(function(e) {
        e.preventDefault();
        console.log('Content link clicked'); // 添加调试日志
        loadContentManagement();
    });

    $('#settings-link').click(function(e) {
        e.preventDefault();
        console.log('Settings link clicked'); // 添加调试日志
        loadSystemSettings();
    });

    // 确保CSRF token可用
    const csrfToken = getCookie('csrftoken');
    console.log('CSRF Token:', csrfToken); // 调试CSRF token
});

function checkAdminStatus() {
    return new Promise((resolve) => {
        // 直接解析，不再检查会话
        $('#admin-name').text('管理员');
        resolve({});
    });
}

function loadDashboard() {
    $.ajax({
        url: '/api/admin/dashboard/',
        type: 'GET',
        success: function(response) {
            if (response && response.stats) {
                console.log('Dashboard data:', response);
                let html = `
                    <div class="dashboard">
                        <h2>系统概览</h2>
                        <div class="stats-container">
                            <div class="stat-card">
                                <div class="stat-icon"><i class="fas fa-users"></i></div>
                                <h3>总用户数</h3>
                                <p class="stat-value">${response.stats.total_users || 0}</p>
                            </div>
                            <div class="stat-card">
                                <div class="stat-icon"><i class="fas fa-user-check"></i></div>
                                <h3>活跃用户</h3>
                                <p class="stat-value">${response.stats.active_users || 0}</p>
                            </div>
                            <div class="stat-card">
                                <div class="stat-icon"><i class="fas fa-user-graduate"></i></div>
                                <h3>专家用户</h3>
                                <p class="stat-value">${response.stats.experts || 0}</p>
                            </div>
                        </div>
                    </div>
                `;
                $('#content-area').html(html);
            } else {
                console.error('Invalid dashboard response:', response);
                $('#content-area').html(`
                    <div class="alert alert-warning">
                        <h4>无法加载仪表盘数据</h4>
                        <p>请检查网络连接或稍后再试</p>
                    </div>
                `);
            }
        },
        error: function(xhr) {
            console.error('Dashboard load failed:', xhr.statusText);
        }
    });
}

function loadUsers() {
    $.ajax({
        url: '/api/admin/users/',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                let html = `
                    <div class="users-management">
                        <h2>用户管理</h2>
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>用户名</th>
                                        <th>邮箱</th>
                                        <th>手机号</th>
                                        <th>用户类型</th>
                                        <th>注册时间</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                `;
                
                response.users.forEach(user => {
                    html += `
                        <tr>
                            <td>${user.id}</td>
                            <td>${user.name}</td>
                            <td>${user.email}</td>
                            <td>${user.phone}</td>
                            <td>${getUserTypeText(user.type)}</td>
                            <td>${user.create_time}</td>
                            <td>
                                <button class="btn btn-sm btn-primary edit-user" data-id="${user.id}">编辑</button>
                                <button class="btn btn-sm btn-danger delete-user" data-id="${user.id}">删除</button>
                            </td>
                        </tr>
                    `;
                });
                
                html += `
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
                
                $('#content-area').html(html);
                
                // 绑定编辑和删除按钮事件
                $('.edit-user').click(function() {
                    const userId = $(this).data('id');
                    editUser(userId);
                });
                
                $('.delete-user').click(function() {
                    const userId = $(this).data('id');
                    deleteUser(userId);
                });
            }
        },
        error: function(xhr) {
            console.error('Users load failed:', xhr.statusText);
        }
    });
}

function getUserTypeText(type) {
    switch(type) {
        case '0': return '管理员';
        case '1': return '普通用户';
        case '2': return '专家';
        default: return '未知';
    }
}

function editUser(userId) {
    // 直接获取用户数据
    $.ajax({
        url: `/api/admin/users/${userId}`,
        type: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        xhrFields: {
            withCredentials: true
        },
        success: function(response) {
            if (!response.success) {
                alert(response.message || '获取用户信息失败');
                return;
            }
            
            // 创建编辑表单模态框
            const modalHtml = `
                <div class="modal fade" id="editUserModal" tabindex="-1" role="dialog">
                    <div class="modal-dialog" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">编辑用户</h5>
                                <button type="button" class="close" data-dismiss="modal">
                                    <span>&times;</span>
                                </button>
                            </div>
                            <div class="modal-body">
                                <form id="editUserForm">
                                    <input type="hidden" id="userId" value="${response.user.id}">
                                    <div class="form-group">
                                        <label for="userName">用户名</label>
                                        <input type="text" class="form-control" id="userName" value="${response.user.name}">
                                    </div>
                                    <div class="form-group">
                                        <label for="userEmail">邮箱</label>
                                        <input type="email" class="form-control" id="userEmail" value="${response.user.email}">
                                    </div>
                                    <div class="form-group">
                                        <label for="userPhone">手机号</label>
                                        <input type="tel" class="form-control" id="userPhone" value="${response.user.phone}">
                                    </div>
                                    <div class="form-group">
                                        <label for="userType">用户类型</label>
                                        <select class="form-control" id="userType">
                                            <option value="0" ${response.user.type === '0' ? 'selected' : ''}>管理员</option>
                                            <option value="1" ${response.user.type === '1' ? 'selected' : ''}>普通用户</option>
                                            <option value="2" ${response.user.type === '2' ? 'selected' : ''}>专家</option>
                                        </select>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-dismiss="modal">取消</button>
                                <button type="button" class="btn btn-primary" id="saveUserBtn">保存</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 添加模态框到DOM
            $('body').append(modalHtml);
            
            // 显示模态框
            $('#editUserModal').modal('show');
            
            // 绑定保存按钮事件
            $('#saveUserBtn').click(function() {
                const userData = {
                    name: $('#userName').val(),
                    email: $('#userEmail').val(),
                    phone: $('#userPhone').val(),
                    type: $('#userType').val()
                };
                
                // 验证表单
                if (!userData.name || !userData.email || !userData.phone) {
                    alert('请填写所有必填字段');
                    return;
                }
                
                // 提交更新
                $.ajax({
            url: `/api/admin/users/${userId}/`,  // 确保URL以斜杠结尾
            type: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    data: JSON.stringify(userData),
                    success: function(response) {
                        if (response.success) {
                            $('#editUserModal').modal('hide');
                            alert('用户信息更新成功');
                            loadUsers();
                        } else {
                            alert(response.message || '更新失败');
                        }
                    },
                    error: function(xhr) {
                        alert('请求失败: ' + xhr.statusText);
                    }
                });
            });
            
            // 模态框关闭时移除
            $('#editUserModal').on('hidden.bs.modal', function() {
                $(this).remove();
            });
        },
        error: function(xhr) {
            alert('请求失败: ' + xhr.statusText);
        }
    });
}

function deleteUser(userId) {
    if (confirm('确定要删除这个用户吗？')) {
        $.ajax({
            url: `/api/admin/users/${userId}`,
            type: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            xhrFields: {
                withCredentials: true
            },
            success: function(response) {
                if (response && response.success) {
                    alert('用户删除成功');
                    loadUsers();
                } else {
                    alert(response.message || '删除失败');
                }
            },
            error: function(xhr, status, error) {
                console.error('Delete user failed:', error);
                alert('删除失败: ' + (xhr.responseJSON?.message || error));
            }
        });
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function loadContentManagement() {
    $.ajax({
        url: '/api/admin/content/',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                let html = `
                    <div class="content-management">
                        <h2>内容管理</h2>
                        <div class="tabs">
                            <button class="tab-btn active" data-tab="posts">论坛帖子</button>
                            <button class="tab-btn" data-tab="questions">专家问答</button>
                        </div>
                        <div class="tab-content active" id="posts-tab">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>标题</th>
                                            <th>作者</th>
                                            <th>发布时间</th>
                                            <th>状态</th>
                                            <th>操作</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                `;

                response.posts.forEach(post => {
                    html += `
                        <tr>
                            <td>${post.id}</td>
                            <td>${post.title}</td>
                            <td>${post.author}</td>
                            <td>${post.create_time}</td>
                            <td>${getContentStatusText(post.status)}</td>
                            <td>
                                <button class="btn btn-sm btn-success approve-content" data-id="${post.id}" data-type="post">通过</button>
                                <button class="btn btn-sm btn-warning reject-content" data-id="${post.id}" data-type="post">拒绝</button>
                                <button class="btn btn-sm btn-danger delete-content" data-id="${post.id}" data-type="post">删除</button>
                            </td>
                        </tr>
                    `;
                });

                html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="tab-content" id="questions-tab">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>标题</th>
                                            <th>作者</th>
                                            <th>发布时间</th>
                                            <th>状态</th>
                                            <th>操作</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                `;

                response.questions.forEach(question => {
                    html += `
                        <tr>
                            <td>${question.id}</td>
                            <td>${question.title}</td>
                            <td>${question.author}</td>
                            <td>${question.create_time}</td>
                            <td>${question.answered ? '已回答' : '待回答'}</td>
                            <td>
                                <button class="btn btn-sm btn-danger delete-content" data-id="${question.id}" data-type="question">删除</button>
                            </td>
                        </tr>
                    `;
                });

                html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `;

                $('#content-area').html(html);

                // 绑定标签页切换事件
                $('.tab-btn').click(function() {
                    const tabId = $(this).data('tab');
                    $('.tab-btn').removeClass('active');
                    $(this).addClass('active');
                    $('.tab-content').removeClass('active');
                    $(`#${tabId}-tab`).addClass('active');
                });

                // 绑定内容操作按钮事件
                $('.approve-content').click(function() {
                    const contentId = $(this).data('id');
                    const contentType = $(this).data('type');
                    manageContent('approve', contentId, contentType);
                });

                $('.reject-content').click(function() {
                    const contentId = $(this).data('id');
                    const contentType = $(this).data('type');
                    manageContent('reject', contentId, contentType);
                });

                $('.delete-content').click(function() {
                    const contentId = $(this).data('id');
                    const contentType = $(this).data('type');
                    manageContent('delete', contentId, contentType);
                });
            }
        },
        error: function(xhr) {
            console.error('Content load failed:', xhr.statusText);
        }
    });
}

function getContentStatusText(status) {
    switch(status) {
        case '0': return '待审核';
        case '1': return '已通过';
        case '2': return '已拒绝';
        default: return '未知';
    }
}

function manageContent(action, contentId, contentType) {
    if (action === 'delete' && !confirm('确定要删除这条内容吗？')) {
        return;
    }

    $.ajax({
        url: '/api/admin/content/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({
            action: action,
            content_id: contentId,
            content_type: contentType
        }),
        success: function(response) {
            if (response.success) {
                alert(response.message);
                loadContentManagement(); // 刷新内容列表
            } else {
                alert(response.message || '操作失败');
            }
        },
        error: function(xhr) {
            alert('请求失败: ' + xhr.statusText);
        }
    });
}

function loadSystemSettings() {
    $.ajax({
        url: '/api/admin/settings/',
        type: 'GET',
        success: function(response) {
            if (response.success) {
                const settings = response.settings;
                let html = `
                    <div class="system-settings">
                        <h2>系统设置</h2>
                        <form id="settings-form">
                            <div class="form-group">
                                <label for="site-name">网站名称</label>
                                <input type="text" class="form-control" id="site-name" value="${settings.site_name}">
                            </div>
                            <div class="form-group form-check">
                                <input type="checkbox" class="form-check-input" id="maintenance-mode" ${settings.maintenance_mode ? 'checked' : ''}>
                                <label class="form-check-label" for="maintenance-mode">维护模式</label>
                            </div>
                            <div class="form-group form-check">
                                <input type="checkbox" class="form-check-input" id="allow-registration" ${settings.allow_registration ? 'checked' : ''}>
                                <label class="form-check-label" for="allow-registration">允许注册</label>
                            </div>
                            <div class="form-group">
                                <label for="default-user-type">默认用户类型</label>
                                <select class="form-control" id="default-user-type">
                                    <option value="0" ${settings.default_user_type === '0' ? 'selected' : ''}>管理员</option>
                                    <option value="1" ${settings.default_user_type === '1' ? 'selected' : ''}>普通用户</option>
                                    <option value="2" ${settings.default_user_type === '2' ? 'selected' : ''}>专家</option>
                                </select>
                            </div>
                            <div class="notification-settings">
                                <h4>通知设置</h4>
                                <div class="form-group form-check">
                                    <input type="checkbox" class="form-check-input" id="email-notifications" ${settings.notification_settings.email_enabled ? 'checked' : ''}>
                                    <label class="form-check-label" for="email-notifications">启用邮件通知</label>
                                </div>
                                <div class="form-group form-check">
                                    <input type="checkbox" class="form-check-input" id="push-notifications" ${settings.notification_settings.push_enabled ? 'checked' : ''}>
                                    <label class="form-check-label" for="push-notifications">启用推送通知</label>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary">保存设置</button>
                        </form>
                    </div>
                `;

                $('#content-area').html(html);

                // 绑定表单提交事件
                $('#settings-form').submit(function(e) {
                    e.preventDefault();
                    saveSystemSettings();
                });
            }
        },
        error: function(xhr) {
            console.error('Settings load failed:', xhr.statusText);
        }
    });
}

function saveSystemSettings() {
    const settings = {
        site_name: $('#site-name').val(),
        maintenance_mode: $('#maintenance-mode').is(':checked'),
        allow_registration: $('#allow-registration').is(':checked'),
        default_user_type: $('#default-user-type').val(),
        notification_settings: {
            email_enabled: $('#email-notifications').is(':checked'),
            push_enabled: $('#push-notifications').is(':checked')
        }
    };

    $.ajax({
        url: '/api/admin/settings/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify(settings),
        success: function(response) {
            if (response.success) {
                alert('系统设置已保存');
            } else {
                alert(response.message || '保存失败');
            }
        },
        error: function(xhr) {
            alert('请求失败: ' + xhr.statusText);
        }
    });
}

function logout() {
    $.ajax({
        url: '/logout',
        type: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function() {
            window.location.href = '/';
        },
        error: function(xhr, status, error) {
            console.error('Logout failed:', error);
            alert('登出失败，请重试');
        }
    });
}
