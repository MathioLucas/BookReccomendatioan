import os

def get_folder_path():
    folder_path = input("Enter the path of the folder: ")
    if not os.path.isdir(folder_path):
        print("The path is not a folder")
        exit()
    print(f"file path is {folder_path}")
    return folder_path