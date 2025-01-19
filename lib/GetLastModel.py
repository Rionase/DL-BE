import os

directory = 'models'

def GetLastModelFile():

    """
    GetLastModelFile

    RETURN THE LAST TRAINED AND SAVED MODELS FILES
    IF NO MODELS FILES FOUND, RETURN FALSE
    """

    # RETURN ARRAY LIST OF FILES INSIDE MODELS DIRECTORY
    listFiles = [filename for filename in os.listdir(directory) if os.path.isfile(os.path.join(directory, filename))]
    if ( len(listFiles) == 0 ) :
        return False

    numbers = [int(filename.split('-')[1].split('.')[0]) for filename in listFiles]
    return f"model-{max(numbers)}.h5"

def GetLastModelCount():

    """
    GetLastModelCount

    RETURN THE LAST INCREMENT COUNT OF SAVED MODELS FILES
    IF NO MODELS FILES FOUND, RETURN FALSE
    """

    # RETURN ARRAY LIST OF FILES INSIDE MODELS DIRECTORY
    listFiles = [filename for filename in os.listdir(directory) if os.path.isfile(os.path.join(directory, filename))]
    if ( len(listFiles) == 0 ) :
        return False

    numbers = [int(filename.split('-')[1].split('.')[0]) for filename in listFiles]
    return max(numbers)