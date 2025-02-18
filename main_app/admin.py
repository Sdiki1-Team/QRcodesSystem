from django.contrib import admin
from django.utils.html import format_html
from .models import Object, Work, Review, WorkImage
from auth_app.models import CustomUser

class WorkInline(admin.TabularInline):
    model = Work
    extra = 0
    fields = ('user', 'start_time', 'end_time', 'work_status')
    readonly_fields = ('work_status',)

    def work_status(self, obj):
        return "В процессе" if obj.end_time is None else "Завершено"
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
    list_display = ('name', 'address', 'deadline', 'status', 'supervisor', 'start_time', 'end_time')
    list_filter = ('status', 'supervisor')
    search_fields = ('name', 'address')
    filter_horizontal = ('worker',)
    inlines = [WorkInline]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "worker":
            kwargs["queryset"] = CustomUser.objects.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    fieldsets = (
        (None, {
            'fields': ('name', 'address', 'task_description')
        }),
        ('Детали', {
            'fields': ('deadline', 'status', 'supervisor', 'worker', 'qr_code')
        }),
        ('Временные метки', {
            'fields': ('start_time', 'end_time'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('id', 'object', 'user', 'start_time', 'end_time', 'duration')
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
    list_display = ('work', 'supervisor', 'rating', 'review_date')
    list_filter = ('rating', 'supervisor')
    raw_id_fields = ('work', 'supervisor')

    fieldsets = (
        (None, {
            'fields': ('work', 'supervisor')
        }),
        ('Оценка', {
            'fields': ('rating', 'comment')
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