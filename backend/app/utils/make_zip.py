import os
import shutil

def zip_directory(directory_path, arch_name):
    
    # Формируем имя ZIP-архива
    zip_filename = f"{directory_path}/{arch_name}"
    
    shutil.make_archive(zip_filename, 'zip', directory_path)