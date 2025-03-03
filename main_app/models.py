from ast import mod
import datetime
from django.db import models
from auth_app.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

class Object(models.Model):
    

    name = models.CharField(max_length=255, verbose_name='Имя')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    task_description = models.TextField(verbose_name='Описание задачи')
    deadline = models.DateTimeField(verbose_name='Срок сдачи')
    worker = models.ManyToManyField(CustomUser, related_name='assigned_objects', blank=True, verbose_name='Работнки')
    supervisor = models.ForeignKey(CustomUser, related_name='supervised_objects', on_delete=models.CASCADE, verbose_name='Ответственный')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='Дата начала')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')
    qr_code = models.URLField(blank=True, null=True, verbose_name='QR код') 

    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"

    def __str__(self):
        return self.name


# Сигнал, который будет генерировать URL для qr_code после сохранения объекта
@receiver(post_save, sender=Object)
def generate_qr_code(sender, instance, created, **kwargs):
    if created:
        instance.qr_code = f"nikitacmo949.ru/get_by_qr/{instance.id}/"
        instance.save()


class Work(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name='Id')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Имя')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    worker_comment = models.TextField(null=True, blank=True, verbose_name='Комментарий работника')
    object = models.ForeignKey(Object, on_delete=models.CASCADE, verbose_name='Объект') 
    user = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Работник')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='Время начала')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='Время окончания')

    def start_work(self, name: str, description: str = None):
        self.start_time = datetime.datetime.now()
        self.name = name
        self.description = description
        self.save()

    def end_work(self):
        self.end_time = datetime.datetime.now()
        self.save()

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

class Review(models.Model):
    work = models.OneToOneField(Work, on_delete=models.CASCADE, verbose_name='Работа')
    supervisor = models.ForeignKey(CustomUser, related_name='reviews', on_delete=models.CASCADE, verbose_name='Кто оценил')
    rating = models.IntegerField(verbose_name='Оценка')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    review_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оценки')

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"

    def __str__(self):
        return f"Review for {self.work.object.name} by {self.supervisor.username}"

class WorkImage(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, verbose_name='Работа')
    image = models.ImageField(upload_to='images/', verbose_name='Изображение')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"
    
