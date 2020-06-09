from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

from datetime import datetime, timedelta, timezone

class Company(models.Model):
	name = models.CharField(max_length=255)

	def __str__(self):
		return self.name

class Worker(models.Model):
	user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE,)
	company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='workers',)
	positions = [
		('director', 'Руководитель'),
		('employee', 'Сотрудник'),
	]
	position = models.CharField(max_length=8, choices=positions, default='employee')

	def __str__(self):
		return str(self.user)

@receiver(post_save, sender=Worker)
def director_group(sender, instance, created, **kwargs):
    if created and instance.position=='director':
        instance.user.groups.add(Group.objects.get(name='directors'))

class Task(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField()	
	creation_time = models.DateTimeField(auto_now_add=True)
	execution_time = models.PositiveSmallIntegerField()
	worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='tasks',)
	statuses = [
		('in_progress', 'Выполняется'),
		('checking', 'На проверке'),
		('done', 'Успешно выполнено'),
		('expired', 'Просрочено'),
	]
	status = models.CharField(max_length=17, choices=statuses)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('task_detail', args=[str(self.id)])

	def get_task_confirm_url(self):
		return reverse('task_confirm', args=[str(self.id)])

	def refresh_status(self):
		if self.status=='in_progress' and (datetime.now(timezone.utc)-self.creation_time)>timedelta(minutes=self.execution_time):
			self.status='expired'
			self.save()

	@property
	def name_status(self):
		return f'{self.title} ({self.get_status_display()})'