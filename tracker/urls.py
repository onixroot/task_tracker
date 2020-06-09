from django.urls import path, include

from .views import (
	ActiveTasks,
	AllTasks,
	TaskDetail,
	TaskConfirm,
	TaskUpdate,
	TaskCreate,
	worker_not_found,
	)

urlpatterns = [
    path('worker_not_found/', worker_not_found, name='worker_not_found'),
	path('', ActiveTasks.as_view(), name='active_tasks_list'),
	path('history/', AllTasks.as_view(), name='all_tasks_list'),
	path('task/<int:pk>/', TaskDetail.as_view(), name='task_detail'),
	path('task/<int:pk>/confirm', TaskConfirm.as_view(), name='task_confirm'),
	path('task/<int:pk>/update', TaskUpdate.as_view(), name='task_update'),
	path('task/create', TaskCreate.as_view(), name='task_create'),
	path('accounts/', include('django.contrib.auth.urls')),
]