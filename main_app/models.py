from ast import mod
import datetime
from django.db import models
from auth_app.models import CustomUser

# Create your models here.
class Object(models.Model):
    STATUS_CHOICES = (
        ('not_started', 'Не начато'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершено'),
    )

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    task_description = models.TextField()
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    worker = models.ManyToManyField(CustomUser, related_name='assigned_objects', blank=True)
    supervisor = models.ForeignKey(CustomUser, related_name='supervised_objects', on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    qr_code = models.URLField(blank=True, null=True)  # Ссылка на QR-код

    def __str__(self):
        return self.name


class Work(models.Model):
    id = models.BigAutoField(primary_key=True)
    object = models.ForeignKey(Object, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def start_work(self):
        self.start_time = datetime.datetime.now()
        self.save()

    def end_work(self):
        self.end_time = datetime.datetime.now()
        self.save()


class Review(models.Model):
    work = models.OneToOneField(Work, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(CustomUser, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.work.object.name} by {self.supervisor.username}"

class WorkImage(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
