import io
import csv
from PIL import Image
from multiprocessing import Pool, cpu_count
from db import LumaDB

# Initialize database
db = LumaDB()
images_db = db.db.images.files


def process_image(image_meta):
    db = LumaDB()  # Create a new instance for each process
    try:
        file_result = db.get_file(image_id)

        if file_result and isinstance(file_result, tuple):
            file_data, file_extension = file_result

            if file_data and file_extension.lower() in ["png", "jpg", "jpeg", "gif", "webp", "svg", "bmp", "ico"]:
                image = Image.open(io.BytesIO(file_data))

                # Resize the image
                aspect_ratio = image.height / image.width
                new_height = int(640 * aspect_ratio)
                resized_image = image.resize((640, new_height))

                # Convert to WebP
                img_byte_arr = io.BytesIO()
                resized_image.save(img_byte_arr, format='WebP', quality=80)
                img_byte_arr = img_byte_arr.getvalue()

                # Save the thumbnail
                db.save_thumbnail(img_byte_arr, image_id)

            else:
                raise ValueError("Invalid file data or unsupported file extension")
        else:
            raise ValueError("File not found or returned data is not valid")
        return True
    except Exception as e:
        return image_id, str(e)


def save_failed_processes(failed_processes):
    with open('failed_image_processing.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['image_id', 'error'])
        for failed in failed_processes:
            writer.writerow(failed)


for image in images_db.find():
    image_id = image["_id"]
    # convert all images to JPEG
    try:
        process_image(image_id)
        print(f"Processed image {image_id}")
    except Exception as e:
        print(f"Failed to process image {image_id}: {e}")
        save_failed_processes([(image_id, e)])

