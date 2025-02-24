from django.urls import path
from .views import GetFreeWorksView, StartWorkView, EndWorkView, ReviewCreateView, WorksWithoutReviewsView, ObjectStatusView, WorkDetailView, WorkImageDeleteView,UserWorksWithReviewsAndImagesView, WorkImageDetailView, WorkImageListView, WorkImageUploadView, WorkHistoryView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('start/', StartWorkView.as_view(), name='start_work'),
    path('end/', EndWorkView.as_view(), name='end_work'),
    path("info/<int:work_id>/", WorkDetailView.as_view(), name="work-detail"),


    path('object/status/<int:object_id>/', ObjectStatusView.as_view(), name='status_object'),
    path('object/work-history/<int:object_id>/', WorkHistoryView.as_view(), name='work-history'),
    path('object/work-free/<int:object_id>/', GetFreeWorksView.as_view(), name='work-free'),

    path('image_work/<int:work_id>/', WorkImageUploadView.as_view(), name='image_upload'),
    path('image_work/<int:work_id>/list/', WorkImageListView.as_view(), name='image_list'),
    path('image_work/<int:work_id>/<int:image_id>/', WorkImageDetailView.as_view(), name='image_detail'),
    path('image_work/<int:work_id>/<int:pk>/delete/', WorkImageDeleteView.as_view(), name='image_delete'),

    path('user/works/', UserWorksWithReviewsAndImagesView.as_view(), name='user-works-with-reviews-and-images'),

    path('review/<int:work_id>/', ReviewCreateView.as_view(), name='create-review'),
    path('works_without_reviews/', WorksWithoutReviewsView.as_view(), name='works-without-reviews'),
]
