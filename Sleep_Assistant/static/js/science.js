$(document).ready(function() {
    // 初始化AOS动画
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });

    // 新文章按钮点击事件
    $('#newSciencePostBtn').click(function() {
        checkLoginStatus().then(function(response) {
            if (response.isAuthenticated) {
                $('#newSciencePostForm').toggle();
                $('#sciencePostsList').toggle();
            } else {
                alert('请先登录后再发表文章');
                $('#signinModal').modal('show');
            }
        }).fail(function() {
            alert('登录状态检查失败');
        });
    });

    // 取消按钮点击事件
    $('#cancelSciencePostBtn').click(function() {
        $('#newSciencePostForm').hide();
        $('#sciencePostsList').show();
    });

    // 检查登录状态
    function checkLoginStatus() {
        return $.get('/api/login/check').then(function(response) {
            return {
                isAuthenticated: response.isAuthenticated,
                user: response.user
            };
        });
    }

    // 加载知识中心文章列表
    function loadSciencePosts() {
        $.get('/api/science/posts/')
            .done(function(data) {
                if(data.posts && data.posts.length > 0) {
                    renderSciencePosts(data.posts);
                    loadPopularPosts(data.posts.slice(0, 5)); // 取前5条作为热门文章
                } else {
                    $('#sciencePostsList').html('<div class="alert alert-info">暂无知识文章，快来分享你的知识吧！</div>');
                }
            })
            .fail(function() {
                $('#sciencePostsList').html('<div class="alert alert-danger">加载文章失败，请刷新重试</div>');
            });
    }

    // 渲染知识中心文章列表 - 更新卡片样式
    function renderSciencePosts(posts) {
        let html = '';
        posts.forEach(post => {
                    html += `
                        <div class="col-lg-4 col-md-6 mb-4">
                            <div class="card science-post-card h-100" data-id="${post.id}">
                                <img src="/static/img/blog-${Math.floor(Math.random() * 6) + 1}.png" class="card-img-top" alt="文章图片">
                                <div class="card-body">
                                    <h5 class="card-title">${post.title}</h5>
                                    <p class="card-text text-muted">${post.summary}</p>
                                </div>
                                <div class="card-footer bg-transparent">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small class="text-muted">
                                            <i class="fas fa-user"></i> ${post.author}
                                        </small>
                                        <a href="/blog/${post.id}/" class="btn btn-sm btn-primary">查看详情</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
        });
        $('#sciencePostsList').html(html);
    }

    // 加载文章详情
    function loadSciencePostDetail(postId) {
        $.get(`/api/science/post/${postId}/`)
            .done(function(data) {
                if(data.post) {
                    const post = data.post;
                    $('#sciencePostImage').attr('src', post.image || '/static/img/blog-1.png');
                    $('#sciencePostAuthor').text(post.author);
                    $('#sciencePostDate').text(post.create_time);
                    $('#sciencePostCommentCount').text(post.comment_count);
                    $('#sciencePostTitle').text(post.title);
                    $('#sciencePostContent').html(post.text); // 显示完整内容
                    $('#sciencePostLikeCount').text(post.like_count);
                    
                    // 显示详情视图
                    $('#sciencePostsList').hide();
                    $('#sciencePostDetail').show();
                }
            })
            .fail(function() {
                alert('加载文章详情失败');
            });
    }

    // 提交新文章 - 确保区分摘要和内容
    $('#sciencePostForm').submit(function(e) {
        e.preventDefault();
        console.log('Form submission started');
        
        const title = $('#form_sciencePostTitle').val().trim();
        const summary = $('#form_sciencePostSummary').val().trim();
        const content = $('#form_sciencePostContent').val().trim();
        
        console.log('Form values:', {title, summary, content});
        
        if(!title || !summary || !content) {
            console.log('Validation failed - empty fields');
            alert('标题、摘要和内容不能为空');
            return;
        }

        const formData = new FormData(this); // 使用表单元素创建FormData
        formData.append('title', title);
        formData.append('summary', summary);
        formData.append('text', content);
        formData.append('doc_type', '3');

        console.log('FormData prepared:', formData);

        $.ajax({
            url: '/api/science/post/create/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function(data) {
                if(data.success) {
                    $('#sciencePostForm')[0].reset();
                    loadSciencePosts();
                }
                alert(data.message);
            },
            error: function() {
                alert('提交失败，请重试');
            }
        });
    });

    // 其他原有功能保持不变...
    loadSciencePosts();
});

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
