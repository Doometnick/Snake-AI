import pickle
import os

FLD = "Results"

DESCRIPTION = "Walls 11-50-3 50Kmry 10ep lr0005"

def load_pickle(file_name):
    try:
        file_name = os.path.join(FLD, DESCRIPTION, file_name)
        return pickle.load(open(file_name, "rb"))
    except:
        return None

def save_pickle(file, name):
    file_name = os.path.join(FLD, DESCRIPTION, name)
    pickle.dump(file, open(file_name, "wb"))

def create_folder(description):
    folder = os.path.join(FLD, description)
    if not os.path.exists(folder):
        os.makedirs(folder)

def get_full_path(filename):
    return os.path.join(FLD, DESCRIPTION, filename)

def exists(file_path):
    return os.path.exists(file_path)
