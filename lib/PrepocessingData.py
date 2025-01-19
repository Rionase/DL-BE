import os
import cv2
from PIL import Image
import shutil
import uuid

dataset_video_organic = 'dataset/Video/Organik'
dataset_video_unorganic = 'dataset/Video/Anorganik'
dataset_foto_organic = 'dataset/Foto/Organik'
dataset_foto_unorganic = 'dataset/Foto/Anorganik'

data_organic = 'data/Oganik'
data_unorganic = 'data/Anorganik'

data_dir = 'data'
image_exts = ['jpeg', 'jpg', 'png']

def CopyFile (source_file, destination_dir) :
    shutil.copy(source_file, destination_dir)
    print("saved to :", destination_dir)

def GetAllFiles(dir_name):

    """
    This function retrieves all files from the specified directory and its subdirectories,
    generating a unique filename for each file in the format IMG_{uuid}.{extension}.

    Return Format : { IMG_{uuid}.{extension} : filePath, ... }

    Args:
        dir_name (str): The path to the directory from which to retrieve files.
    """

    listFile = {}
    for root, dirs, files in os.walk(dir_name):
        # 'root' is the current directory path
        # 'dirs' is the list of subdirectories in 'root'
        # 'files' is the list of files in 'root'
        
        for file in files:
            file_path = os.path.join(root, file)
            # Get the original file extension
            _, extension = os.path.splitext(file)
            # Generate a unique filename in the format IMG_{uuid}.{extension}
            unique_file_name = f"IMG_{uuid.uuid4()}{extension}"
            listFile[unique_file_name] = file_path 

    return listFile

def SplitVideoToImage(file_name, video_path, output_dir, frame_interval = 30):
    """
    Splits a video into images at the specified frame interval, skipping the first and last 10 seconds.
    
    Args:
        video_path (str): Path to the input video file.
        output_dir (str): Directory to save extracted images.
        frame_interval (int): Number of frames to skip between each saved image.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get the video frame rate and total frames
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate frames to skip: 10 seconds at start and 10 seconds at end
    skip_seconds = 10
    start_frame = int(fps * skip_seconds)  # Frames to skip at the beginning (10 seconds)
    end_frame = total_frames - int(fps * skip_seconds)  # Ending frame to stop before the last 10 seconds

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)  # Start at the frame after 10 seconds

    frame_count = start_frame
    image_count = 0
    
    while frame_count < end_frame:
        ret, frame = cap.read()
        if not ret:
            break  # Exit when video ends

        # Save image if the current frame is at the specified interval
        if (frame_count - start_frame) % frame_interval == 0:
            # Get the filename without extention
            base_image = os.path.splitext(file_name)[0]
            image_filename = os.path.join(output_dir, f"{base_image}_frame_{image_count:04d}.jpg")
            print("saved to:", image_filename)
            cv2.imwrite(image_filename, frame)
            image_count += 1

        frame_count += 1
    
    cap.release()

def OrganizeDataset () :

    # ORGANIZE ORGANIC PHOTO
    organicPhoto = GetAllFiles(dataset_foto_organic)
    for fileName, filePath in organicPhoto.items():
        CopyFile(filePath, f"{data_organic}/{fileName}")

    # ORGANIZE UNORGANIC PHOTO
    unorganicPhoto = GetAllFiles(dataset_foto_unorganic)
    for fileName, filePath in unorganicPhoto.items():
        CopyFile(filePath, f"{data_unorganic}/{fileName}")

    # ORGANIZE ORGANIC VIDEO
    organicVideo = GetAllFiles(dataset_video_organic)
    for fileName, filePath in organicVideo.items():
        SplitVideoToImage(fileName, filePath, data_organic, 60)

    # ORGANIZE UNORGANIC VIDEO
    unorganicVideo = GetAllFiles(dataset_video_unorganic)
    for fileName, filePath in unorganicVideo.items():
        SplitVideoToImage(fileName, filePath, data_unorganic, 60)

def RemoveDodgyImage() :
    """
    Removes unwanted images from the specified directory.

    This function goes through each image in subdirectories of `data_dir`. For each image:
      - Attempts to open it to confirm it is a valid file.
      - Checks if the image has an extension of jpeg, jpg, or png.
      - If the image cannot be opened or does not have an allowed extension, it is deleted.
    """

    for image_class in os.listdir(data_dir):
        for image in os.listdir(os.path.join(data_dir, image_class)):
            image_path = os.path.join(data_dir, image_class, image)
            try:
                img = cv2.imread(image_path)
                with Image.open(image_path) as img_file:
                    img_format = img_file.format.lower()
                if img_format not in image_exts:
                    print('Image not in ext list {}'.format(image_path))
                    os.remove(image_path)
            except Exception as e:
                print('Issue with image {}'.format(image_path))
                os.remove(image_path)

    print("LOG : Success Removing Dodgy Image")
