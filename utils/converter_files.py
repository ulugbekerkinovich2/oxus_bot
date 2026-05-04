from pillow_heif import register_heif_opener
from PIL import Image

register_heif_opener()


def convert_heic_to_jpg(input_path):
    output_path = input_path.rsplit('.', 1)[0] + ".jpg"
    image = Image.open(input_path)
    image.save(output_path, "JPEG")
    return output_path
