
from django.urls import path
from .views import UploadAPIView, HistoryAPIView, PDFExportView

urlpatterns = [
    path('upload/', UploadAPIView.as_view(), name='api-upload'),
    path('history/', HistoryAPIView.as_view(), name='api-history'),
    path('report/<int:pk>/', PDFExportView.as_view(), name='api-report'),
]
