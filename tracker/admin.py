from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Company, Worker, Task

class WorkerInline(admin.TabularInline):
    model = Worker

class CompanyAdmin(admin.ModelAdmin):
    inlines = [WorkerInline,]

class TaskInLine(admin.TabularInline):
	model = Task

class WorkerAdmin(admin.ModelAdmin):
	inlines = [TaskInLine,]
	list_display = ('user', 'company', 'position')

admin.site.register(Company, CompanyAdmin)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(Task)