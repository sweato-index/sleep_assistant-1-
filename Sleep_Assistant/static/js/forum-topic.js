// 论坛帖子详情页功能
document.addEventListener('DOMContentLoaded', function() {
    // 获取帖子ID - 从URL参数或路径中获取
    let postId = new URLSearchParams(window.location.search).get('post');
    if (!postId) {
        const pathParts = window.location.pathname.split('/').filter(Boolean);
        postId = pathParts[pathParts.length - 1];
    }
    if (!postId) {
        console.error('无法获取帖子ID');
        return;
    }
    const csrftoken = getCookie('csrftoken');

    // 加载帖子详情
    function loadPostDetail() {
        fetch(`/api/forum/post/${postId}/`)
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error('加载帖子失败:', data.message || '未知错误');
                    alert('加载帖子详情失败，请稍后重试');
                    return;
                }
                document.getElementById('post-title').textContent = data.title;
                document.getElementById('post-text').textContent = data.content;
                document.getElementById('post-author-name').textContent = data.author;
                document.getElementById('post-create-time').textContent = data.create_time;
                document.getElementById('like-count').textContent = data.like_count;
                document.getElementById('favorite-count').textContent = data.favorite_count;

                // 更新点赞/收藏按钮状态
                if (data.user_actions) {
                    if (data.user_actions.liked) {
                        document.getElementById('like-btn').classList.add('active');
                    }
                    if (data.user_actions.favorited) {
                        document.getElementById('favorite-btn').classList.add('active');
                    }
                }
            });
    }

    // 加载评论
    function loadComments() {
        fetch(`/api/forum/post/${postId}/`)
            .then(response => response.json())
            .then(data => {
                const commentList = document.getElementById('comment-list');
                commentList.innerHTML = '';

                data.comments.forEach(comment => {
                    const commentElement = document.createElement('div');
                    commentElement.className = 'media mb-4';
                    commentElement.innerHTML = `
                        <img src="/static/img/author-2.png" class="mr-3 rounded-circle" width="50" alt="${comment.author}">
                        <div class="media-body">
                            <h5 class="mt-0">${comment.author}</h5>
                            <p>${comment.content}</p>
                            <small class="text-muted">${comment.create_time}</small>
                            <div class="mt-2">
                                <a href="#" class="btn btn-sm btn-outline-primary">回复</a>
                                <span class="ml-2">${comment.reply_count} 条回复</span>
                            </div>
                        </div>
                    `;
                    commentList.appendChild(commentElement);
                });
            });
    }

    // 点赞功能
    document.getElementById('like-btn').addEventListener('click', function() {
        fetch(`/api/forum/post/${postId}/like/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('like-count').textContent = data.like_count;
                this.classList.toggle('active');
            }
        });
    });

    // 收藏功能
    document.getElementById('favorite-btn').addEventListener('click', function() {
        fetch(`/api/forum/post/${postId}/favorite/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('favorite-count').textContent = data.favorite_count;
                this.classList.toggle('active');
            }
        });
    });

    // 提交评论
    document.getElementById('comment-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const content = document.getElementById('comment-text').value.trim();
        
        if (!content) {
            alert('评论内容不能为空');
            return;
        }

        fetch(`/api/forum/post/${postId}/comment/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ content: content })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('comment-text').value = '';
                loadComments();
            }
        });
    });

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

    // 初始化加载
    loadPostDetail();
    loadComments();
});
