from django.contrib import admin
from django.utils.html import format_html
from .models import Object, Work, Review, WorkImage
from auth_app.models import CustomUser
import qrcode
import base64
from django.urls import path
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

class WorkInline(admin.TabularInline):
    model = Work
    extra = 0
    fields = ('name', 'description', 'start_time', 'end_time', 'work_status')
    readonly_fields = ('work_status', 'start_time', 'end_time')

    def work_status(self, obj):
        return "Не начата" if obj.start_time is None else "В процессе" if obj.end_time is None else "Завершено"
    work_status.short_description = "Статус работы"

class WorkImageInline(admin.TabularInline):
    model = WorkImage
    extra = 0
    fields = ('image_preview', 'uploaded_at')
    readonly_fields = ('image_preview', 'uploaded_at')

    def image_preview(self, obj):
        return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url) if obj.image else ""
    image_preview.short_description = "Превью"

@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    class Media:
        js = ('admin.js', )
    list_display = ('name', 'address', 'deadline', 'my_status', 'supervisor', 'start_time', 'end_time', 'qr_code_link')
    search_fields = ('name', 'address')
    filter_horizontal = ('worker',)
    inlines = [WorkInline]
    
    class Media:
        js = ('admin.js', )
    
    def qr_code_link(self, obj):
        if obj.qr_code:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(obj.qr_code)  #
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_code_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # Вставляем base64-код в тег <img> для отображения
            return format_html('<img src="data:image/png;base64,{}" style="max-height: 100px;" />', qr_code_base64)

    qr_code_link.short_description = 'QR Code'

    readonly_fields = ('qr_code', 'qr_code_link', 'qr_code_download', 'my_status')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "worker":
            kwargs["queryset"] = CustomUser.objects.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('download_qr/<int:object_id>/', self.admin_site.admin_view(self.download_qr_code), name='download_qr'),  # Правильный URL для скачивания
        ]
        return custom_urls + urls

    def download_qr_code(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj and obj.qr_code:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(obj.qr_code)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            buffered.seek(0)
            response = HttpResponse(buffered, content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="qr_code_{object_id}.png"'
            return response
        return HttpResponse("QR Code not found", status=404)
    
    def my_status(self, obj):
        works = Work.objects.filter(object=obj)

        if not works.exists() or all(work.start_time is None for work in works):
            return format_html(
                '<span style="display: inline-block; width: 12px; height: 12px; background-color: red; border-radius: 50%; margin-right: 8px;"></span>'
                '<span>Не начато</span>'
            )

        if all(work.end_time is not None for work in works):
            return format_html(
                '<span style="display: inline-block; width: 12px; height: 12px; background-color: green; border-radius: 50%; margin-right: 8px;"></span>'
                '<span>Завершено</span>'
            )

        return format_html(
            '<span style="display: inline-block; width: 12px; height: 12px; background-color: yellow; border-radius: 50%; margin-right: 8px;"></span>'
            '<span>В процессе</span>'
        )

    my_status.short_description = 'Статус' 


    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        custom_fieldsets = list(fieldsets)
        return custom_fieldsets

    def qr_code_download(self, obj):
        if obj.qr_code:
            download_url = f"/admin/main_app/object/download_qr/{obj.id}/"
            return format_html('<a class="button" href="{}">Download QR Code</a>', download_url)
        return "QR код не доступен"

    qr_code_download.short_description = "Download QR Code"

    fieldsets = (
        (None, {
            'fields': ('name', 'address', 'task_description')
        }),
        ('Детали', {
            'fields': ('deadline', 'my_status', 'supervisor', 'worker', 'qr_code', 'qr_code_link', 'qr_code_download')
        }),
        ('Временные метки', {
            'fields': ('start_time', 'end_time'),
            'classes': ('collapse',)
        }),
    )



@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('name', 'object', 'user', 'start_time', 'end_time', 'duration')
    list_filter = ('user', 'object')
    search_fields = ('id', 'object__name')
    inlines = [WorkImageInline]
    actions = ['end_work']

    def duration(self, obj):
        if obj.start_time and obj.end_time:
            return obj.end_time - obj.start_time
        return "В процессе"
    duration.short_description = "Длительность"

    def end_work(self, request, queryset):
        for work in queryset:
            if work.end_time is None:
                work.end_work()
    end_work.short_description = "Завершить выбранные работы"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('work_name', 'supervisor', 'rating', 'review_date')
    list_filter = ('rating', 'supervisor')
    raw_id_fields = ('work', 'supervisor')
    readonly_fields = ('work_name', 'work_description', 'work_images', 'work_start_time', 'work_end_time', 'work_worker_comment', 'worker_name', 'worker_username')
    

    def work_name(self, obj):
        return obj.work.name if obj.work else "Не указано"
    work_name.short_description = "Название работы"

    def work_description(self, obj):
        return obj.work.description if obj.work else "Не указано"
    work_description.short_description = "Описание работы"

    def work_start_time(self, obj):
        return obj.work.start_time if obj.work else "Не указано"
    work_start_time.short_description = "Время начала"

    def work_end_time(self, obj):
        return obj.work.end_time if obj.work else "Не указано"
    work_end_time.short_description = "Время окончания"

    def work_worker_comment(self, obj):
        return obj.work.worker_comment if obj.work else "Не указано"
    work_worker_comment.short_description = "Комментарий работника"

    def worker_name(self, obj):
        return obj.work.user.fullname if obj.work and obj.work.user else "Не указано"
    worker_name.short_description = "Имя работника"

    def worker_username(self, obj):
        return obj.work.user.username if obj.work and obj.work.user else "Не указано"
    worker_username.short_description = "Ник работника"

    def work_images(self, obj):

        if obj.work and obj.work.workimage_set.exists():
            images = obj.work.workimage_set.all() 
            return format_html(
                '<br>'.join([format_html('<img src="{}" style="max-height: 100px; margin-right: 5px;"/>', image.image.url) for image in images])
            )
        return 'Не указано'
    work_images.short_description = "Изображения работы"

    fieldsets = (
        ('Информация о работнике', {
            'fields': ('worker_name', 'worker_username')
        }),
        ('Оценка', {
            'fields': ('rating', 'comment')
        }),
        ('Информация о работе', {
            'fields': ('work_name', 'work_description', 'work_start_time', 'work_end_time', 'work_worker_comment', 'work_images'),
        }),
    )




@admin.register(WorkImage)
class WorkImageAdmin(admin.ModelAdmin):
    list_display = ('work', 'uploaded_at', 'image_preview')
    list_filter = ('work__user', 'work__object')
    search_fields = ('work__id',)
    readonly_fields = ('uploaded_at', 'image_preview')

    def image_preview(self, obj):
        return format_html('<img src="{}" style="max-height: 200px;"/>', obj.image.url) if obj.image else ""
    image_preview.short_description = "Превью"

    def has_add_permission(self, request):
        # Запрет добавления изображений через админку
        return False
    

admin.site.unregister(Group)
admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)