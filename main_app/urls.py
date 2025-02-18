from django.urls import path
from .views import StartWorkView, EndWorkView, ReviewView, ObjectStatusView, WorkImageDeleteView, WorkImageDetailView, WorkImageListView, WorkImageUploadView, WorkHistoryView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('start/', StartWorkView.as_view(), name='start_work'),
    path('end/', EndWorkView.as_view(), name='end_work'),
    path('review/<int:work_id>/', ReviewView.as_view(), name='add_review'),

    path('object/status/<int:object_id>/', ObjectStatusView.as_view(), name='status_object'),
    path('object/work-history/<int:object_id>/', WorkHistoryView.as_view(), name='work-history'),
    
    path('image_work/<int:work_id>/', WorkImageUploadView.as_view(), name='image_upload'),
    path('image_work/<int:work_id>/list/', WorkImageListView.as_view(), name='image_list'),
    path('image_work/<int:work_id>/<int:image_id>/', WorkImageDetailView.as_view(), name='image_detail'),
    path('image_work/<int:work_id>/<int:pk>/delete/', WorkImageDeleteView.as_view(), name='image_delete'),
]
