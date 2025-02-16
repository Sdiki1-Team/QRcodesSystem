from django.urls import path
from .views import StartWorkView, EndWorkView, ReviewView

urlpatterns = [
    path('start/', StartWorkView.as_view(), name='start_work'),
    path('end/', EndWorkView.as_view(), name='end_work'),
    path('review/<int:work_id>/', ReviewView.as_view(), name='add_review'),
]
