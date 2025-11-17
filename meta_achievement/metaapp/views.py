from django.shortcuts import render, HttpResponse
from .models import Achievement, Criteria, ChildCriteria

# Create your views here.
def achievement_list(request):
    achievements = Achievement.objects.all()
    return HttpResponse(achievements)