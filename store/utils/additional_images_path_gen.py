import os
from uuid import uuid4


def generate_additional_image_path(self, filename):
    # self - экземпляр модели Product
    # filename - имя загруженного файла

    # Разбиваем имя файла и его расширение
    ext = filename.split('.')[-1]

    # Генерируем уникальное имя для файла с помощью UUID
    unique_filename = f"{uuid4()}.{ext}"

    # Папка, в которой будут храниться дополнительные изображения
    folder = 'products_additional_images'

    # Полный путь сохранения изображения
    path = os.path.join(folder, self.name, unique_filename)

    return path