from django.urls import path
from .views import PredictImages, PredictZipImages, ListTrainedModels

urlpatterns = [
    path('predict-image', PredictImages.as_view(), name="predict-image"),
    path('predict-zip-image', PredictZipImages.as_view(), name='predict-zip-image'),
    path('list-trained-models', ListTrainedModels.as_view(), name='list-trained-models')
]
