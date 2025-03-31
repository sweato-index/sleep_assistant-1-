from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "index.html")

def science(request):
    return render(request, "science.html")

def tracker(request):
    return render(request, "tracker.html")

def assessment(request):
    return render(request, "assessment.html")

def advice(request):
    return render(request, "advice.html")

def community(request):
    return render(request, "community.html")

def profile(request):
    return render(request, "profile.html")

def blog_details(request):
    return render(request, "blog-details.html")

def ai_assistant(request):
    return render(request, "ai-assistant.html")

def forum_topic(request):
    return render(request, "forum-topic.html")