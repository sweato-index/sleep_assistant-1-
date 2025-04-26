$(document).ready(function() {
    // 初始化挑战功能
    initChallengeFeatures();

    function initChallengeFeatures() {
        loadChallenges();
        loadUserChallenges();
        setupChallengeEventHandlers();
    }

    // 加载挑战列表
    function loadChallenges() {
        $.get('/api/challenges/')
            .done(function(data) {
                if(data.success && data.challenges.length > 0) {
                    renderChallenges(data.challenges);
                } else {
                    $('#challengesList').html('<div class="alert alert-info">暂无挑战活动</div>');
                }
            })
            .fail(function() {
                $('#challengesList').html('<div class="alert alert-danger">加载挑战失败</div>');
            });
    }

    // 加载用户参与的挑战
    function loadUserChallenges() {
        $.get('/api/challenge/user/')
            .done(function(data) {
                if(data.success) {
                    renderUserChallenges(data.challenges);
                } else {
                    $('#userChallengesList').html('<div class="alert alert-info">您当前没有参与任何挑战</div>');
                }
            })
            .fail(function() {
                $('#userChallengesList').html('<div class="alert alert-danger">加载挑战进度失败</div>');
            });
    }

    // 渲染挑战列表
    function renderChallenges(challenges) {
        let html = '';
        challenges.forEach(challenge => {
            const progressPercent = Math.round((challenge.completed_days / challenge.total_days) * 100);
            
            const isExpired = challenge.is_expired;
            const isCheckedInToday = challenge.is_checked_in_today;
            
            html += `
                <div class="card mb-3 challenge-item ${isExpired ? 'challenge-expired' : ''}" 
                     data-id="${challenge.challenge_id}">
                    <div class="card-body">
                        <h5 class="card-title">${challenge.title}</h5>
                        <p class="card-text">${challenge.description}</p>
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <small class="text-muted">
                                <i class="fas fa-user"></i> ${challenge.initiator}
                                <i class="fas fa-calendar ml-2"></i> ${challenge.start_date} 至 ${challenge.end_date}
                            </small>
                            <div>
                                ${isExpired ? 
                                    '<span class="badge badge-secondary">已过期</span>' : 
                                    `<span class="badge badge-${challenge.joined ? 'success' : 'secondary'}">
                                        ${challenge.joined ? '已参加' : '未参加'}
                                    </span>`}
                            </div>
                        </div>
                        <div class="progress mb-2">
                            <div class="progress-bar" role="progressbar" 
                                style="width: ${progressPercent}%" 
                                aria-valuenow="${progressPercent}" 
                                aria-valuemin="0" 
                                aria-valuemax="100">
                                ${challenge.completed_days}/${challenge.total_days}天
                            </div>
                        </div>
                        <div class="challenge-actions">
                            ${challenge.joined ? 
                                `<button class="btn btn-sm btn-outline-danger leave-challenge" ${isExpired ? 'disabled' : ''}>
                                    退出挑战
                                </button>
                                <button class="btn btn-sm ${isCheckedInToday ? 'btn-success checked-in' : 'btn-primary'} checkin-challenge ml-2" 
                                    ${isExpired || isCheckedInToday ? 'disabled' : ''}>
                                    ${isCheckedInToday ? '已打卡' : '今日打卡'}
                                </button>` : 
                                `<button class="btn btn-sm btn-success join-challenge" ${isExpired ? 'disabled' : ''}>
                                    加入挑战
                                </button>`}
                        </div>
                        ${challenge.last_checkin_date ? 
                            `<small class="text-muted d-block mt-2">
                                <i class="fas fa-calendar-check"></i> 上次打卡: ${challenge.last_checkin_date}
                            </small>` : ''}
                    </div>
                </div>
            `;
        });
        $('#challengesList').html(html);
    }

    // 渲染用户挑战列表
    function renderUserChallenges(challenges) {
        let html = '';
        challenges.forEach(challenge => {
            const progressPercent = Math.round((challenge.completed_days / challenge.total_days) * 100);
            const progressClass = challenge.is_expired ? 'bg-secondary' : 'bg-success';
            
            html += `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${challenge.title}</h5>
                        <p class="card-text text-muted small">
                            ${challenge.start_date} 至 ${challenge.end_date}
                            ${challenge.is_expired ? '<span class="badge bg-danger float-end">已结束</span>' : ''}
                        </p>
                        <div class="progress mb-2">
                            <div class="progress-bar ${progressClass}" 
                                 role="progressbar" 
                                 style="width: ${progressPercent}%" 
                                 aria-valuenow="${progressPercent}" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                                ${challenge.completed_days}/${challenge.total_days}天
                            </div>
                        </div>
                        ${challenge.last_checkin_date ? 
                            `<p class="small mb-0">上次打卡: ${challenge.last_checkin_date}</p>` : ''}
                        ${challenge.is_checked_in_today ? 
                            `<p class="small text-success mb-0"><i class="fas fa-check-circle"></i> 今日已打卡</p>` : ''}
                    </div>
                </div>
            `;
        });
        $('#userChallengesList').html(html);
    }

    // 设置事件处理器
    function setupChallengeEventHandlers() {
        // 创建挑战表单提交
        $('#newChallengeForm').submit(function(e) {
            e.preventDefault();
            const title = $('#challengeTitle').val().trim();
            const description = $('#challengeDescription').val().trim();
            const startDate = $('#challengeStartDate').val();
            const endDate = $('#challengeEndDate').val();
            
            if(!title || !startDate || !endDate) {
                alert('请填写完整信息');
                return;
            }

            const submitBtn = $(this).find('button[type="submit"]');
            submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> 提交中...');

            $.ajax({
                url: '/api/challenge/create/',
                method: 'POST',
                contentType: 'application/json',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                },
                data: JSON.stringify({
                    title: title,
                    description: description,
                    start_date: startDate,
                    end_date: endDate
                })
            }).done(function(data) {
                if(data.success) {
                    $('#newChallengeForm')[0].reset();
                    $('#newChallengeModal').modal('hide');
                    loadChallenges();
                    loadUserChallenges();
                    showToast('success', data.message);
                } else {
                    showToast('error', data.message);
                }
            }).fail(function(xhr) {
                const msg = xhr.responseJSON?.message || '创建挑战失败';
                showToast('error', msg);
            }).always(function() {
                submitBtn.prop('disabled', false).text('创建挑战');
            });
        });

        // 加入挑战
        $(document).on('click', '.join-challenge', function() {
            const challengeId = $(this).closest('.challenge-item').data('id');
            const btn = $(this);
            btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> 处理中...');

            $.ajax({
                url: `/api/challenge/${challengeId}/join/`,
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            }).done(function(data) {
                if(data.success) {
                    loadChallenges();
                    loadUserChallenges();
                    showToast('success', data.message);
                } else {
                    showToast('error', data.message);
                }
            }).fail(function(xhr) {
                const msg = xhr.responseJSON?.message || '加入挑战失败';
                showToast('error', msg);
            }).always(function() {
                btn.prop('disabled', false).text('加入挑战');
            });
        });

        // 退出挑战
        $(document).on('click', '.leave-challenge', function() {
            if(!confirm('确定要退出该挑战吗？')) return;
            
            const challengeId = $(this).closest('.challenge-item').data('id');
            const btn = $(this);
            btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> 处理中...');

            $.ajax({
                url: `/api/challenge/${challengeId}/leave/`,
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            }).done(function(data) {
                if(data.success) {
                    loadChallenges();
                    loadUserChallenges();
                    showToast('success', data.message);
                } else {
                    showToast('error', data.message);
                }
            }).fail(function(xhr) {
                const msg = xhr.responseJSON?.message || '退出挑战失败';
                showToast('error', msg);
            }).always(function() {
                btn.prop('disabled', false).text('退出挑战');
            });
        });

        // 打卡
        $(document).on('click', '.checkin-challenge', function() {
            const challengeId = $(this).closest('.challenge-item').data('id');
            const btn = $(this);
            btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> 打卡中...');

            $.ajax({
                url: `/api/challenge/${challengeId}/checkin/`,
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            }).done(function(data) {
                if(data.success) {
                    loadChallenges();
                    loadUserChallenges();
                    showToast('success', data.message);
                    
                    // 更新按钮状态为已打卡
                    btn.removeClass('btn-primary').addClass('btn-success checked-in')
                       .text('已打卡').prop('disabled', true);
                } else {
                    showToast('error', data.message);
                    btn.prop('disabled', false).text('今日打卡');
                }
            }).fail(function(xhr) {
                const msg = xhr.responseJSON?.message || '打卡失败';
                showToast('error', msg);
                btn.prop('disabled', false).text('今日打卡');
            });
        });

        // 新挑战按钮点击
        $('#newChallengeBtn').click(function() {
            checkLoginStatus().done(function(data) {
                if(data.isAuthenticated) {
                    $('#newChallengeModal').modal('show');
                } else {
                    $('#signinModal').modal('show');
                }
            });
        });
    }

    // 显示Toast通知
    function showToast(type, message) {
        const toast = $(`
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `);
        $('#toastContainer').append(toast);
        toast.toast({ autohide: true, delay: 3000 });
        toast.toast('show');
        toast.on('hidden.bs.toast', function() {
            $(this).remove();
        });
    }

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
                if (cookie.substring(0, 10) === ('csrftoken=')) {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
