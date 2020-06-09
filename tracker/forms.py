from django import forms

from .models import Worker, Task

class TaskCreateForm(forms.ModelForm):
	title = forms.CharField(max_length=255, label='Заголовок')
	description = forms.CharField(widget=forms.Textarea, label='Описание')
	execution_time = forms.IntegerField(label='Время на выполнение (мин.)')
	worker = forms.ModelChoiceField(queryset=Worker.objects.none(), label='Назначить на сотрудника')

	class Meta:
		model = Task
		fields = ['title', 'description', 'execution_time', 'worker',]

	def __init__(self, worker_qs, *args, **kwargs):
		super(TaskCreateForm, self).__init__(*args, **kwargs)
		self.fields['worker'].queryset = worker_qs

	def save(self, commit=True):
		model = super(TaskCreateForm, self).save(commit=False)
		model.status = 'in_progress'
		if commit:
			model.save()
		return model

class TaskUpdateForm(forms.ModelForm):
	statuses = [
		('in_progress', 'Вернуть на выполнение'),
		('done', 'Подтвердить выполнение'),
	]
	status = forms.ChoiceField(choices=statuses, label='Статус')

	class Meta:
		model = Task
		fields = ('status',)