import zipfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from lib.PredictImage import PredictImage
import os

# Allowed file extensions
ALLOWED_EXTENSIONS = ['jpeg', 'jpg', 'png']
MAX_FILE_SIZE_MB = 50

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