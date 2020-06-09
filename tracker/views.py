from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from .models import Worker, Task
from .forms import TaskCreateForm, TaskUpdateForm

class ActiveTasks(LoginRequiredMixin, ListView):
	model = Task
	template_name = 'active_tasks_list.html'
	context_object_name = 'tasks'

	def dispatch(self, request, *args, **kwargs):
		user = self.request.user
		if user.is_authenticated:
			try:
				user.worker
				return super().dispatch(request, *args, **kwargs)
			except get_user_model().worker.RelatedObjectDoesNotExist:
				return redirect('worker_not_found')
		return redirect('login')

	def get_queryset(self):
		worker = self.request.user.worker
		if worker.position=='director':
			tasks = Task.objects.filter( Q(worker__company=worker.company)&Q(status='in_progress') )
			(task.refresh_status() for task in tasks)
			tasks = Task.objects.filter(worker__company=worker.company)
		elif worker.position=='employee':
			tasks = worker.tasks.all().filter(status='in_progress')
			(task.refresh_status() for task in worker.tasks.all())
			tasks = tasks.filter(status='in_progress')
		return tasks.order_by('-creation_time')

def worker_not_found(request):
	return render(request, 'base.html')

class AllTasks(LoginRequiredMixin, ListView):
	model = Task
	template_name = 'all_tasks_list.html'
	context_object_name = 'tasks'
	paginate_by = 5

	def get_queryset(self):
		worker = self.request.user.worker
		if worker.position=='director':
			tasks = Task.objects.filter( Q(worker__company=worker.company)&Q(status='in_progress') )
			(task.refresh_status() for task in tasks)
			tasks = Task.objects.filter(worker__company=worker.company)
		elif worker.position=='employee':
			tasks = worker.tasks.all()
			(task.refresh_status() for task in tasks)
		return tasks.order_by('-creation_time')

class TaskConfirm(LoginRequiredMixin, DetailView):
	model = Task
	template_name = 'task_confirm.html'

	def dispatch(self, request, *args, **kwargs):
		task = self.get_object()
		task.refresh_status()
		worker = self.request.user.worker
		if worker==task.worker and task.status=='in_progress':
			return super().dispatch(request, *args, **kwargs)
		elif worker==task.worker:
			return redirect(task)
		raise PermissionDenied

	def post(self, request, *args, **kwargs):
		task = self.get_object()
		task.status='checking'
		task.save()
		return redirect('active_tasks_list')

class TaskDetail(LoginRequiredMixin, DetailView):
	model = Task
	template_name = 'task_detail.html'

	def dispatch(self, request, *args, **kwargs):
		task = self.get_object()
		task.refresh_status()
		worker = self.request.user.worker
		if worker==task.worker or is_director(worker, task):
			return super().dispatch(request, *args, **kwargs)
		raise PermissionDenied

def is_director(worker, task):
	t_company = task.worker.company
	w_company = worker.company
	dir_group = worker.user.groups.filter(name='directors')
	if t_company==w_company and dir_group:
		return True

class TaskUpdate(UpdateView):
	model = Task
	form_class = TaskUpdateForm
	template_name = 'task_update.html'

	def dispatch(self, request, *args, **kwargs):
		task = self.get_object()
		worker = self.request.user.worker
		if is_director(worker, task) and task.status=='checking':
			return super().dispatch(request, *args, **kwargs)
		elif is_director(worker, task):
			return redirect(task)
		raise PermissionDenied

class TaskCreate(PermissionRequiredMixin, CreateView):
	form_class = TaskCreateForm
	template_name = 'task_create.html'
	permission_required = 'tracker.add_task'

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		company = self.request.user.worker.company
		kwargs['worker_qs'] = Worker.objects.filter( Q(company=company)&Q(position='employee') )
		return kwargs