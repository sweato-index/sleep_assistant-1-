$(document).ready(function() {
    // 初始化AOS动画
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });

    // 处理页面加载时的锚点跳转
    if(window.location.hash) {
        const target = $(window.location.hash);
        if(target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 800);
        }
    }

    // // 处理导航栏点击事件
    // $('.dropdown-menu a').click(function(e) {
    //     const target = $(this).attr('href');
        
    //     // 滚动到目标位置
    //     if(target.startsWith('#')) {
    //         e.preventDefault();
    //         $('html, body').animate({
    //             scrollTop: $(target).offset().top - 100
    //         }, 800);
    //     }
    // });

    // 初始化tab切换
    $('.nav-tabs a').click(function(e) {
        const target = $(this).attr('href');
        console.log('Tab link clicked:', target);
        
        // 只阻止以#开头的链接的默认行为
        if(target && target.startsWith('#')) {
            console.log('Preventing default for anchor link');
            e.preventDefault();
            $(this).tab('show');
            $('html, body').animate({
                scrollTop: $(target).offset().top - 100
            }, 800);
        }
        // 其他链接保持默认行为
    });

    // 确保AI助手按钮正常工作
    $('a[href="ai-assistant.html"]').click(function(e) {
        console.log('AI Assistant link clicked');
        // 确保不阻止默认行为
        return true;
    });

    // 处理表单提交
    $('form').submit(function(e) {
        e.preventDefault();
        const form = $(this);
        const formType = form.attr('id') || form.find('button[type="submit"]').text();
        
        // 显示加载状态
        const submitBtn = form.find('button[type="submit"]');
        submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> 提交中...');

        // 模拟提交
        setTimeout(() => {
            submitBtn.prop('disabled', false).text('提交成功');
            setTimeout(() => {
                submitBtn.text(submitBtn.data('original-text') || '提交');
            }, 2000);
        }, 1500);
    });

    // 处理加入群组按钮
    $('.group-item button').click(function() {
        const btn = $(this);
        btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> 加入中...');
        
        setTimeout(() => {
            btn.text('已加入').removeClass('btn-primary').addClass('btn-success');
        }, 1500);
    });

    // 处理挑战进度
    function updateChallengeProgress() {
        $('.challenge-progress .progress-bar').each(function() {
            const progress = $(this);
            const percent = progress.attr('aria-valuenow');
            progress.css('width', percent + '%');
        });
    }

    // 初始化
    updateChallengeProgress();

    // 新增论坛功能
    // 处理评论提交
    $('.comments-section form').submit(function(e) {
        e.preventDefault();
        const textarea = $(this).find('textarea');
        const comment = textarea.val().trim();
        
        if(comment.length === 0) {
            alert('请输入评论内容');
            return;
        }

        const newComment = `
            <div class="media mb-4">
                <img src="assets/img/author-1.png" class="mr-3 rounded-circle" width="50" alt="新用户">
                <div class="media-body">
                    <h5 class="mt-0">新用户</h5>
                    <p>${comment}</p>
                    <small class="text-muted">刚刚</small>
                    <div class="mt-2">
                        <a href="#" class="btn btn-sm btn-outline-primary">回复</a>
                        <a href="#" class="btn btn-sm btn-outline-success ml-2">点赞 (0)</a>
                    </div>
                </div>
            </div>
        `;

        $('.comment-list').prepend(newComment);
        textarea.val('');
    });

    // 处理点赞功能
    $(document).on('click', '.btn-outline-success', function(e) {
        e.preventDefault();
        const btn = $(this);
        let count = parseInt(btn.text().match(/\d+/)[0]) || 0;
        count++;
        btn.text(`点赞 (${count})`);
    });

    // 处理回复功能
    $(document).on('click', '.btn-outline-primary', function(e) {
        e.preventDefault();
        const comment = $(this).closest('.media');
        const replyForm = `
            <div class="media mt-3 ml-5">
                <div class="media-body">
                    <form class="reply-form">
                        <div class="form-group">
                            <textarea class="form-control" rows="2" placeholder="写下你的回复..."></textarea>
                        </div>
                        <button type="submit" class="btn btn-sm btn-primary">提交回复</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary cancel-reply">取消</button>
                    </form>
                </div>
            </div>
        `;
        
        comment.after(replyForm);
    });

    // 处理取消回复
    $(document).on('click', '.cancel-reply', function() {
        $(this).closest('.media').remove();
    });

    // 处理回复提交
    $(document).on('submit', '.reply-form', function(e) {
        e.preventDefault();
        const textarea = $(this).find('textarea');
        const reply = textarea.val().trim();
        
        if(reply.length === 0) {
            alert('请输入回复内容');
            return;
        }

        const newReply = `
            <div class="media mt-3 ml-5">
                <img src="assets/img/author-2.png" class="mr-3 rounded-circle" width="40" alt="回复用户">
                <div class="media-body">
                    <h6 class="mt-0">回复用户</h6>
                    <p>${reply}</p>
                    <small class="text-muted">刚刚</small>
                    <div class="mt-2">
                        <a href="#" class="btn btn-sm btn-outline-primary">回复</a>
                        <a href="#" class="btn btn-sm btn-outline-success ml-2">点赞 (0)</a>
                    </div>
                </div>
            </div>
        `;

        $(this).closest('.media').replaceWith(newReply);
    });
});
