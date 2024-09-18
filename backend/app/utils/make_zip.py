import os
import shutil

def zip_directory(directory_path):
    # Получаем имя директории без пути
    directory_name = os.path.basename(directory_path)
    
    # Формируем имя ZIP-архива
    zip_filename = f"{directory_path}/{directory_name}"
    
    shutil.make_archive(zip_filename, 'zip', directory_path)