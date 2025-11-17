from django.contrib import admin
from .models import Achievement, Criteria, ChildCriteria

# Register your models here.
admin.site.register(Achievement)
admin.site.register(Criteria)
admin.site.register(ChildCriteria)