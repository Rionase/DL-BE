import zipfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from lib.PredictImage import PredictImage
from lib.PrepocessingData import OrganizeDataset, RemoveDodgyImage
from lib.ModelingAndTrain import ModelingAndTrain
from lib.GetLastModel import GetLastModelFile
from django.http import FileResponse, Http404
import uuid
import os

# Allowed file extensions
ALLOWED_EXTENSIONS = ['jpeg', 'jpg', 'png']
MAX_FILE_SIZE_MB = 50

dataset_video_organic = 'dataset/Video/Organik'
dataset_video_unorganic = 'dataset/Video/Anorganik'
dataset_foto_organic = 'dataset/Foto/Organik'
dataset_foto_unorganic = 'dataset/Foto/Anorganik'

data_organic = 'data/Organik'
data_unorganic = 'data/Anorganik'

# Base directory for datasets
BASE_DATASET_DIRECTORY = "dataset"  # Path to your dataset folder   

class PredictImages(APIView):
    parser_classes = [MultiPartParser]  # Ensure the API accepts multipart file uploads

    def post(self, request, *args, **kwargs):
        # Get the model from the request body
        model_name = request.data.get('models')
        if not model_name:
            return Response({"error": "Model name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if files are included in the request
        if not request.FILES:
            return Response({"error": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_files = request.FILES.getlist("files")  # Use "files" key for single/multiple uploads
        predictions = []  # To store information about processed files

        try:
            for file in uploaded_files:
                # Validate file format
                file_extension = file.name.split('.')[-1].lower()
                if file_extension not in ALLOWED_EXTENSIONS:
                    return Response(
                        {"error": f"Invalid file format for '{file.name}'. Allowed formats: {ALLOWED_EXTENSIONS}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Process file content (without saving to disk)
                content = file.read()  # Read file content directly into memory
                file_size = len(content)  # Get the size of the file in bytes

                result = PredictImage(content, model_name)
                predictions.append({
                    "file_name": file.name,
                    "prediction": result,
                })

            return Response(
                {
                    "message": "Files processed successfully.",
                    "data": predictions,  # Details of processed files
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PredictZipImages(APIView):
    parser_classes = [MultiPartParser]  # Ensure the API accepts multipart file uploads

    def post(self, request, *args, **kwargs):
        # Get the model from the request body
        model_name = request.data.get('models')
        if not model_name:
            return Response({"error": "Model name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a file is uploaded
        # if 'file' not in request.FILES:
        #     return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']

        # Check if the uploaded file is a ZIP file
        if not zipfile.is_zipfile(uploaded_file):
            return Response({"error": "Uploaded file is not a valid ZIP archive."}, status=status.HTTP_400_BAD_REQUEST)

        # Check file size (convert bytes to MB)
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            return Response(
                {"error": f"File size exceeds the limit of {MAX_FILE_SIZE_MB}MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Process the ZIP file
        try:
            with zipfile.ZipFile(uploaded_file) as zip_file:
                invalid_files = []
                predictions = []  # Store predictions for valid files
                for file_name in zip_file.namelist():
                    # Skip directories
                    if file_name.endswith('/'):
                        continue

                    # Check file extension
                    file_extension = file_name.split('.')[-1].lower()
                    if file_extension not in ALLOWED_EXTENSIONS:
                        invalid_files.append(file_name)
                        continue

                    # Read file content and process
                    with zip_file.open(file_name) as file:
                        content = file.read()  # Read the file content
                        prediction = PredictImage(content, model_name)  # Use PredictImage function
                        predictions.append({
                            "file_name": file_name,
                            "prediction": prediction,
                        })

                if invalid_files:
                    return Response(
                        {
                            "message": "The ZIP file contains invalid files.",
                            "invalid_files": invalid_files,
                            "predictions": predictions,  # Valid files processed
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                return Response(
                    {
                        "message": "All files in the ZIP archive are valid.",
                        "predictions": predictions,
                    },
                    status=status.HTTP_200_OK,
                )
        except zipfile.BadZipFile:
            return Response({"error": "Invalid ZIP file."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListTrainedModels(APIView):
    def get(self, request, *args, **kwargs):
        # Define the path to the "models" folder at the project root
        root_path = os.getcwd()  # Current working directory, which contains "manage.py"
        models_folder_path = os.path.join(root_path, "models")

        # Check if the "models" folder exists
        if not os.path.exists(models_folder_path):
            return Response(
                {"error": "'models' folder not found in the project root."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # List all files in the "models" folder
            files = [
                f for f in os.listdir(models_folder_path)
                if os.path.isfile(os.path.join(models_folder_path, f))
            ]

            python_files = [f for f in files]

            return Response(
                {"files": python_files},  # Return the list of files
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class GetUnprocessedDatasetView(APIView):
    def get(self, request, *args, **kwargs):
        # Helper function to get files with full paths from a directory
        def get_files_from_directory(directory_path):
            if not os.path.exists(directory_path):
                return []
            return [
                os.path.join(directory_path, f).replace("\\", "/")  # Replace backslash with forward slash
                for f in os.listdir(directory_path)
                if os.path.isfile(os.path.join(directory_path, f))
            ]


        try:
            # Collect files with full paths from each directory
            photo_organic_files = get_files_from_directory(dataset_foto_organic)
            photo_unorganic_files = get_files_from_directory(dataset_foto_unorganic)

            # Build the response
            data = {
                "organic": photo_organic_files,
                "unorganic": photo_unorganic_files,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetDatasetImageView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the relative path from the URL
        relative_path = kwargs.get('path', None)
        if not relative_path:
            return Response({"error": "Path parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Construct the full path to the file
        full_path = os.path.join(BASE_DATASET_DIRECTORY, relative_path)

        # Check if the file exists and directly return it
        if os.path.exists(full_path) and os.path.isfile(full_path):
            response = FileResponse(open(full_path, 'rb'), content_type='image/*')
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(full_path)}"'
            return response

        # If file not found, return 404
        raise Http404("File not found.")

class DeleteDatasetImageView(APIView):
    def delete(self, request, *args, **kwargs):
        # Get the relative path from the URL
        relative_path = kwargs.get('path', None)
        if not relative_path:
            return Response({"error": "Path parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Construct the full path to the file
        full_path = os.path.join(relative_path)

        # Check if the file exists and delete it
        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                os.remove(full_path)
                return Response({"message": "File deleted successfully."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If file not found, return 404
        raise Http404("File not found.")

class UploadDataset(APIView):
    parser_classes = [MultiPartParser]  # To handle file uploads

    def post(self, request, *args, **kwargs):
        # Get the 'tipe_sampah' parameter
        tipe_sampah = request.data.get("tipe_sampah", "").lower()
        if tipe_sampah not in ["organik", "anorganik"]:
            return Response(
                {"error": "Invalid 'tipe_sampah'. Must be 'Organik' or 'Anorganik'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

       # Check if files are included in the request
        if not request.FILES:
            return Response({"error": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_files = request.FILES.getlist("files")

        folder_path = ""
        saved_files = [] 

        # Determine the folder path based on tipe_sampah
        if ( tipe_sampah == "organik" ) :
            folder_path = dataset_foto_organic
        elif ( tipe_sampah == "anorganik" ) :
            folder_path = dataset_foto_unorganic

        try:
            for file in uploaded_files:
                # Validate file format
                file_extension = file.name.split('.')[-1].lower()
                if file_extension not in ALLOWED_EXTENSIONS:
                    return Response(
                        {"error": f"Invalid file format for '{file.name}'. Allowed formats: {ALLOWED_EXTENSIONS}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Generate a unique filename in the format IMG_{uuid}.{extension}
                unique_file_name = f"IMG_{uuid.uuid4()}.{file_extension}"

                file_path = os.path.join(folder_path, unique_file_name)
                with open(file_path, "wb") as f:
                    for chunk in file.chunks():
                        f.write(chunk)

                # Add saved file info
                saved_files.append({
                    "original_name": file.name,
                    "saved_name": unique_file_name,
                    "file_path": file_path,
                })

        except Exception as e:
            return Response({"error": f"An error occurred while saving files: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "message": f"{len(saved_files)} file(s) uploaded successfully to {folder_path}.",
                "files": saved_files,
            },
            status=status.HTTP_201_CREATED,
        )

class PrepocessingDataset(APIView):
    def post(self, request, *args, **kwargs):
        try:
            OrganizeDataset()
            errorLogs = RemoveDodgyImage()

        except Exception as e:
            return Response({"error": f"An error occurred while prepocessing data: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "message": f"successfully prepocessing dataset",
                "error_logs" : errorLogs
            },
            status=status.HTTP_201_CREATED,
        )
        
class TrainModel(APIView):
    def post(self, request, *args, **kwargs):
        try:
            ModelingAndTrain()
        except Exception as e:
            return Response({"error": f"An error occurred while training model: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                "message": f"successfully train new model : {GetLastModelFile()}",
            },
            status=status.HTTP_201_CREATED,
        )

class GetProcessedData(APIView):
    def get(self, request, *args, **kwargs):
        # Helper function to get files with full paths from a directory
        def get_files_from_directory(directory_path):
            if not os.path.exists(directory_path):
                return []
            return [
                os.path.join(directory_path, f).replace("\\", "/")  # Replace backslash with forward slash
                for f in os.listdir(directory_path)
                if os.path.isfile(os.path.join(directory_path, f))
            ]
        data = []

        try:
            # Collect files with full paths from each directory
            photo_organic_files = get_files_from_directory(data_organic)
            photo_unorganic_files = get_files_from_directory(data_unorganic)

            for item in photo_organic_files:
                data.append({
                    "file_name": item,
                    "type": 'organic'
                })

            for item in photo_unorganic_files:
                data.append({
                    "file_name": item, 
                    "type": 'unorganic'
                })

            # Build the response

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)