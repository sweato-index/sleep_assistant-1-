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
