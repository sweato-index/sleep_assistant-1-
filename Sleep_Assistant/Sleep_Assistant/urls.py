"""
URL configuration for Sleep_Assistant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp.views import (
    home, science, tracker, assessment, 
    advice, community, profile, blog_details,
    ai_assistant, forum_topic, get_all_user_ids,
    register, login, logout, check_session,
    forum_posts, create_post, post_detail, 
    add_comment, toggle_like, toggle_favorite,
    save_ai_qa, create_group, get_groups,
    join_group, leave_group, get_group_chat,
    send_group_message,expert_questions,
    create_question, question_detail,
    answer_question
)
from myapp.sleep_challenge_views import (
    get_challenges, create_challenge,
    join_challenge, leave_challenge,
    checkin_challenge, get_challenge_progress,
    get_user_challenges
)
from myapp.stress_views import predict_stress, render_stress_assessment
from myapp.views import (
    admin_dashboard, get_users, 
    update_user, delete_user
)

urlpatterns = [
    # 自定义管理员路由
    path('api/admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('api/admin/users/', get_users, name='get_users'),
    path('api/admin/users/<str:user_id>/', update_user, name='update_user'),
    path('api/admin/users/<str:user_id>/delete/', delete_user, name='delete_user'),
    path('django-admin/', admin.site.urls),  # 修改Django admin后台路径
    path('', home, name='home'),
    path('science/', science, name='science'),
    path('tracker/', tracker, name='tracker'),
    path('assessment/', assessment, name='assessment'),
    path('advice/', advice, name='advice'),
    path('community/', community, name='community'),
    path('profile/', profile, name='profile'),
    path('blog-details/', blog_details, name='blog_details'),
    path('ai-assistant/', ai_assistant, name='ai_assistant'),
    path('stress-assessment/', render_stress_assessment, name='stress_assessment'),
    path('forum-topic/<str:post_id>/', forum_topic, name='forum_topic'),
    path('api/user_ids/', get_all_user_ids, name='get_all_user_ids'),
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
    path('api/logout/', logout, name='logout'),
    path('api/login/check/', check_session, name='check_session'),
    path('api/forum/posts/', forum_posts, name='forum_posts'),
    path('api/forum/post/create/', create_post, name='create_post'),
    path('api/forum/post/<str:post_id>/', post_detail, name='post_detail'),
    path('api/forum/post/<str:post_id>/comment/', add_comment, name='add_comment'),
    path('api/forum/post/<str:post_id>/like/', toggle_like, name='toggle_like'),
    path('api/forum/post/<str:post_id>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('api/ai/qa/', save_ai_qa, name='save_ai_qa'),
    # 群组功能路由
    path('api/group/create/', create_group, name='create_group'),
    path('api/groups/', get_groups, name='get_groups'),
    path('api/group/<str:group_id>/join/', join_group, name='join_group'),
    path('api/group/<str:group_id>/leave/', leave_group, name='leave_group'),
    path('api/group/<str:group_id>/chat/', get_group_chat, name='get_group_chat'),
    path('api/group/<str:group_id>/message/', send_group_message, name='send_group_message'),
    # 睡眠挑战功能路由
    path('api/challenges/', get_challenges, name='get_challenges'),
    path('api/challenge/create/', create_challenge, name='create_challenge'),
    path('api/challenge/<str:challenge_id>/join/', join_challenge, name='join_challenge'),
    path('api/challenge/<str:challenge_id>/leave/', leave_challenge, name='leave_challenge'),
    path('api/challenge/<str:challenge_id>/checkin/', checkin_challenge, name='checkin_challenge'),
    path('api/challenge/user/', get_user_challenges, name='get_user_challenges'),
    path('api/challenge/<str:challenge_id>/progress/', get_challenge_progress, name='get_challenge_progress'),
    # 压力评估功能路由
    path('api/predict-stress/', predict_stress, name='predict_stress'),
    # 专家问答功能路由
    path('api/expert/questions/', expert_questions, name='expert_questions'),
    path('api/expert/question/create/', create_question, name='create_question'),
    path('api/expert/question/<str:question_id>/', question_detail, name='question_detail'),
    path('api/expert/question/<str:question_id>/answer/', answer_question, name='answer_question'),
]
