$(document).ready(function() {
    // 初始化AOS动画
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });

    // 检查登录状态
    function checkLoginStatus() {
        return $.get('/api/login/check');
    }

    // 加载帖子列表
    function loadPosts() {
        $.get('/api/forum/posts/')
            .done(function(data) {
                if(data.posts && data.posts.length > 0) {
                    renderPosts(data.posts);
                    loadHotTopics(data.posts.slice(0, 5)); // 取前5条作为热门话题
                } else {
                    $('#postsList').html('<div class="alert alert-info">暂无帖子，快来发表第一个吧！</div>');
                }
            })
            .fail(function() {
                $('#postsList').html('<div class="alert alert-danger">加载帖子失败，请刷新重试</div>');
            });
    }

    // 渲染帖子列表
    function renderPosts(posts) {
        let html = '';
        posts.forEach(post => {
            html += `
                <div class="card mb-3 post-item" data-id="${post.id}">
                    <div class="card-body">
                        <h5 class="card-title">${post.title}</h5>
                        <p class="card-text">${post.summary}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-user"></i> ${post.author} 
                                <i class="fas fa-clock ml-2"></i> ${post.create_time}
                                <i class="fas fa-comment ml-2"></i> ${post.comment_count}条评论
                            </small>
                            <a href="/forum-topic/${post.id}" class="btn btn-sm btn-outline-primary">查看详情</a>
                        </div>
                    </div>
                </div>
            `;
        });
        $('#postsList').html(html);
    }

    // 加载热门话题
    function loadHotTopics(posts) {
        let html = '';
        posts.forEach(post => {
            html += `<li><a href="/forum-topic/?post=${post.id}">${post.title}</a></li>`;
        });
        $('#hotTopics').html(html);
    }

    // 新帖子按钮点击事件
    $('#newPostBtn').click(function() {
        console.log('发表新帖按钮被点击');
        checkLoginStatus().done(function(data) {
            console.log('登录状态检查结果:', data);
            if(data.isAuthenticated) {
                console.log('用户已登录，显示表单');
                $('#newPostForm').slideDown('fast', function() {
                    console.log('表单显示完成');
                });
                $('#newPostBtn').hide();
            } else {
                console.log('用户未登录，显示登录模态框');
                $('#signinModal').modal('show');
            }
        }).fail(function(err) {
            console.error('登录状态检查失败:', err);
        });
    });

    // 取消发帖
    $('#cancelPostBtn').click(function() {
        $('#postForm')[0].reset();
        $('#newPostForm').slideUp();
        $('#newPostBtn').show();
    });

    // 提交新帖子
    $('#postForm').submit(function(e) {
        e.preventDefault();
        const title = $('#postTitle').val().trim();
        const content = $('#postContent').val().trim();
        
        if(!title || !content) {
            alert('标题和内容不能为空');
            return;
        }

        const submitBtn = $(this).find('button[type="submit"]');
        submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> 提交中...');

        // 获取CSRF token
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
        const csrftoken = getCookie('csrftoken');
        
        $.ajax({
            url: '/api/forum/post/create/',
            method: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: JSON.stringify({
                title: title,
                content: content
            })
        }).done(function(data) {
            if(data.success) {
                $('#postForm')[0].reset();
                $('#newPostForm').slideUp();
                $('#newPostBtn').show();
                loadPosts(); // 重新加载帖子列表
            }
            alert(data.message);
        }).fail(function() {
            alert('提交失败，请重试');
        }).always(function() {
            submitBtn.prop('disabled', false).text('提交');
        });
    });

    // 初始化加载帖子
    loadPosts();

    // 其他原有功能保持不变
    if(window.location.hash) {
        const target = $(window.location.hash);
        if(target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 800);
        }
    }

    $('.nav-tabs a').click(function(e) {
        const target = $(this).attr('href');
        if(target && target.startsWith('#')) {
            e.preventDefault();
            $(this).tab('show');
            $('html, body').animate({
                scrollTop: $(target).offset().top - 100
            }, 800);
        }
    });

    // 处理挑战进度
    function updateChallengeProgress() {
        $('.challenge-progress .progress-bar').each(function() {
            const progress = $(this);
            const percent = progress.attr('aria-valuenow');
            progress.css('width', percent + '%');
        });
    }
    updateChallengeProgress();
});
