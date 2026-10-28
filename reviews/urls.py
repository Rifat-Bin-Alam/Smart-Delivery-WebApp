from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.ReviewListView.as_view(), name='review_list'),
    path('write/<int:order_pk>/<int:product_pk>/', views.ReviewCreateView.as_view(), name='review_create'),
    path('admin/', views.AdminReviewModerationView.as_view(), name='admin_review_list'),
]
