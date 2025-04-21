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
    save_ai_qa
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('science/', science, name='science'),
    path('tracker/', tracker, name='tracker'),
    path('assessment/', assessment, name='assessment'),
    path('advice/', advice, name='advice'),
    path('community/', community, name='community'),
    path('profile/', profile, name='profile'),
    path('blog-details/', blog_details, name='blog_details'),
    path('ai-assistant/', ai_assistant, name='ai_assistant'),
    path('forum-topic/<str:post_id>/', forum_topic, name='forum_topic'),
    path('api/user_ids/', get_all_user_ids, name='get_all_user_ids'),
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
    path('api/logout/', logout, name='logout'),
    path('api/login/check', check_session, name='check_session'),
    path('api/forum/posts/', forum_posts, name='forum_posts'),
    path('api/forum/post/create/', create_post, name='create_post'),
    path('api/forum/post/<str:post_id>/', post_detail, name='post_detail'),
    path('api/forum/post/<str:post_id>/comment/', add_comment, name='add_comment'),
    path('api/forum/post/<str:post_id>/like/', toggle_like, name='toggle_like'),
    path('api/forum/post/<str:post_id>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('api/ai/qa/', save_ai_qa, name='save_ai_qa'),
]
