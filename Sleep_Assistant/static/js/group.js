$(document).ready(function() {
    // 检查登录状态
    function checkLoginStatus() {
        return $.get('/api/login/check');
    }

    // 获取CSRF token
    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // 加载群组列表
    function loadGroups() {
        checkLoginStatus().done(function(data) {
            if(data.isAuthenticated) {
                $.get('/api/groups/')
                    .done(function(data) {
                        if(data.success && data.groups.length > 0) {
                            renderGroups(data.groups);
                            loadRecommendedGroups(data.groups.filter(g => !g.role));
                        } else {
                            $('#groupsList').html('<div class="alert alert-info">暂无群组，快来创建第一个吧！</div>');
                        }
                    })
                    .fail(function() {
                        $('#groupsList').html('<div class="alert alert-danger">加载群组失败，请刷新重试</div>');
                    });
            } else {
                $('#groupsList').html('<div class="alert alert-warning">请先登录查看群组</div>');
            }
        });
    }

    // 渲染群组列表
    function renderGroups(groups) {
        let html = '';
        groups.forEach(group => {
            const isMember = group.role !== null;
            html += `
                <div class="card mb-3 group-item" data-id="${group.group_id}">
                    <div class="card-body">
                        <h5 class="card-title">${group.group_name}</h5>
                        <p class="card-text">${group.description}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-users"></i> ${group.member_count}人 
                                <i class="fas fa-clock ml-2"></i> ${group.create_time}
                            </small>
                            ${isMember ? 
                                `<button class="btn btn-sm btn-outline-primary enter-group-btn">进入群聊</button>
                                 ${group.role === '1' ? '<span class="badge badge-success ml-2">管理员</span>' : ''}` : 
                                `<button class="btn btn-sm btn-primary join-group-btn">加入群组</button>`}
                        </div>
                    </div>
                </div>
            `;
        });
        $('#groupsList').html(html);
    }

    // 加载推荐群组
    function loadRecommendedGroups(groups) {
        let html = '';
        groups.slice(0, 3).forEach(group => {
            html += `
                <div class="card mb-2">
                    <div class="card-body p-2">
                        <h6 class="card-title">${group.group_name}</h6>
                        <p class="card-text small">${group.description}</p>
                        <button class="btn btn-sm btn-block btn-outline-primary join-group-btn" 
                                data-id="${group.group_id}">加入群组</button>
                    </div>
                </div>
            `;
        });
        $('#recommendedGroups').html(html || '<p class="text-muted small">暂无推荐群组</p>');
    }

    // 新群组按钮点击事件
    $('#newGroupBtn').click(function() {
        checkLoginStatus().done(function(data) {
            if(data.isAuthenticated) {
                $('#newGroupForm').slideDown();
                $('#newGroupBtn').hide();
            } else {
                $('#signinModal').modal('show');
            }
        });
    });

    // 取消创建群组
    $('#cancelGroupBtn').click(function() {
        $('#groupForm')[0].reset();
        $('#newGroupForm').slideUp();
        $('#newGroupBtn').show();
    });

    // 提交新群组
    $('#groupForm').submit(function(e) {
        e.preventDefault();
        const name = $('#groupName').val().trim();
        const desc = $('#groupDesc').val().trim();
        
        if(!name || !desc) {
            alert('群组名称和描述不能为空');
            return;
        }

        const submitBtn = $(this).find('button[type="submit"]');
        submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> 创建中...');

        $.ajax({
            url: '/api/group/create/',
            method: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            data: JSON.stringify({
                group_name: name,
                description: desc
            })
        }).done(function(data) {
            if(data.success) {
                $('#groupForm')[0].reset();
                $('#newGroupForm').slideUp();
                $('#newGroupBtn').show();
                loadGroups();
            }
            alert(data.message);
        }).fail(function() {
            alert('创建失败，请重试');
        }).always(function() {
            submitBtn.prop('disabled', false).text('创建');
        });
    });

    // 加入群组
    $(document).on('click', '.join-group-btn', function() {
        const groupId = $(this).closest('.group-item').data('id') || $(this).data('id');
        checkLoginStatus().done(function(data) {
            if(data.isAuthenticated) {
                $.ajax({
                    url: `/api/group/${groupId}/join/`,
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken()
                    }
                }).done(function(data) {
                    if(data.success) {
                        loadGroups();
                    }
                    alert(data.message);
                }).fail(function() {
                    alert('加入群组失败');
                });
            } else {
                $('#signinModal').modal('show');
            }
        });
    });

    // 进入群聊
    $(document).on('click', '.enter-group-btn', function() {
        const groupId = $(this).closest('.group-item').data('id');
        const groupName = $(this).closest('.group-item').find('.card-title').text();
        
        $('#chatGroupName').text(groupName);
        $('#groupChatContainer').show();
        $('#groupInfoSidebar').hide();
        loadGroupChat(groupId);
    });

    // 加载群组聊天
    function loadGroupChat(groupId) {
        $.get(`/api/group/${groupId}/chat/`)
            .done(function(data) {
                if(data.success) {
                    renderChatMessages(data.messages.reverse());
                    currentGroupId = groupId;
                    // 设置定时刷新
                    if(chatRefreshInterval) clearInterval(chatRefreshInterval);
                    chatRefreshInterval = setInterval(() => {
                        refreshChatMessages(groupId);
                    }, 5000);
                }
            })
            .fail(function() {
                $('#chatMessages').html('<div class="alert alert-danger">加载聊天失败</div>');
            });
    }

    // 渲染聊天消息
    function renderChatMessages(messages) {
        let html = '';
        messages.forEach(msg => {
                    // 转换时间为北京时间
                    const beijingTime = new Date(msg.create_time);
                    beijingTime.setHours(beijingTime.getHours() + 8);
                    const formattedTime = beijingTime.toLocaleString('zh-CN', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                        hour12: false
                    });
                    
                    html += `
                        <div class="message ${msg.user_id === currentUserId ? 'my-message' : ''}">
                            <div class="message-header">
                                <strong>${msg.user_name}</strong>
                                <small class="text-muted ml-2">${formattedTime}</small>
                            </div>
                            <div class="message-content">${msg.content}</div>
                        </div>
                    `;
        });
        $('#chatMessages').html(html);
        $('#chatMessages').scrollTop($('#chatMessages')[0].scrollHeight);
    }

    // 刷新聊天消息
    function refreshChatMessages(groupId) {
        $.get(`/api/group/${groupId}/chat/`)
            .done(function(data) {
                if(data.success) {
                    renderChatMessages(data.messages.reverse());
                }
            });
    }

    // 发送消息
    $('#sendMessageForm').submit(function(e) {
        e.preventDefault();
        const message = $('#messageInput').val().trim();
        if(!message || !currentGroupId) return;

        $.ajax({
            url: `/api/group/${currentGroupId}/message/`,
            method: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            data: JSON.stringify({
                content: message,
                msg_type: '0'
            })
        }).done(function(data) {
            if(data.success) {
                $('#messageInput').val('');
                refreshChatMessages(currentGroupId);
            }
        }).fail(function() {
            alert('发送失败');
        });
    });

    // 退出群组
    $('#leaveGroupBtn').click(function() {
        if(!currentGroupId) return;
        
        if(confirm('确定要退出该群组吗？')) {
            $.ajax({
                url: `/api/group/${currentGroupId}/leave/`,
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            }).done(function(data) {
                if(data.success) {
                    $('#groupChatContainer').hide();
                    $('#groupInfoSidebar').show();
                    loadGroups();
                }
                alert(data.message);
            }).fail(function() {
                alert('操作失败');
            });
        }
    });

    // 初始化变量
    let currentGroupId = null;
    let currentUserId = null;
    let chatRefreshInterval = null;

    // 获取当前用户ID
    checkLoginStatus().done(function(data) {
        if(data.isAuthenticated) {
            currentUserId = data.user.id;
        }
    });

    // 标签页切换时加载群组
    $('a[data-toggle="tab"][href="#groups"]').on('shown.bs.tab', function() {
        loadGroups();
    });

    // 页面加载时如果直接访问群组标签则加载
    if(window.location.hash === '#groups') {
        loadGroups();
    }
});
