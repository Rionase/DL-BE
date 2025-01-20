from django.urls import path, re_path
from .views import PredictImages, PredictZipImages, ListTrainedModels, GetUnprocessedDatasetView, GetDatasetImageView, DeleteDatasetImageView, UploadDataset, PrepocessingDataset, GetProcessedData, GetDataImageView, GetModels, GetModelValidationImage, TrainModel

urlpatterns = [
    re_path(r'^delete-image/(?P<path>.+)$', DeleteDatasetImageView.as_view(), name='delete-dataset-image'),
    re_path(r'^dataset/(?P<path>.*)$', GetDatasetImageView.as_view(), name='get-dataset-image'),
    re_path(r'^data/(?P<path>.*)$', GetDataImageView.as_view(), name='get-data-image'),
    re_path(r'^validation/(?P<path>.*)$', GetModelValidationImage.as_view(), name='get-model-validation'),
    path('predict-image', PredictImages.as_view(), name="predict-image"),
    path('predict-zip-image', PredictZipImages.as_view(), name='predict-zip-image'),
    path('list-trained-models', ListTrainedModels.as_view(), name='list-trained-models'),
    path('get-unprocessed-dataset', GetUnprocessedDatasetView.as_view(), name='get-unprocessed-dataset'),
    path('upload-dataset', UploadDataset.as_view(), name='upload-dataset'),
    path('prepocessing', PrepocessingDataset.as_view(), name='prepocessing'),
    path('get-processed-data', GetProcessedData.as_view(), name='get-processed-data'),
    path('get-model-data', GetModels.as_view(), name="get-models"),
    path('train', TrainModel.as_view(), name="train-model")
]
