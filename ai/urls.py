from django.urls import path, re_path
from .views import PredictImages, PredictZipImages, ListTrainedModels, GetUnprocessedDatasetView, GetDatasetImageView, DeleteDatasetImageView, UploadDataset, PrepocessingDataset, GetProcessedData

urlpatterns = [
    re_path(r'^delete-image/(?P<path>.+)$', DeleteDatasetImageView.as_view(), name='delete-dataset-image'),
    re_path(r'^dataset/(?P<path>.*)$', GetDatasetImageView.as_view(), name='get-dataset-image'),
    path('predict-image', PredictImages.as_view(), name="predict-image"),
    path('predict-zip-image', PredictZipImages.as_view(), name='predict-zip-image'),
    path('list-trained-models', ListTrainedModels.as_view(), name='list-trained-models'),
    path('get-unprocessed-dataset', GetUnprocessedDatasetView.as_view(), name='get-unprocessed-dataset'),
    path('upload-dataset', UploadDataset.as_view(), name='upload-dataset'),
    path('prepocessing', PrepocessingDataset.as_view(), name='prepocessing'),
    path('get-processed-data', GetProcessedData.as_view(), name='get-processed-data')
]
