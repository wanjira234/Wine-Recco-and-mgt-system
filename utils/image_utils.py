import os
import uuid
from PIL import Image
from flask import current_app
import boto3
from botocore.exceptions import ClientError

class ImageUtils:
    @staticmethod
    def generate_unique_filename(original_filename):
        """
        Generate a unique filename for uploaded images
        """
        ext = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        return unique_filename

    @staticmethod
    def resize_image(image_path, max_size=(800, 800)):
        """
        Resize image while maintaining aspect ratio
        """
        with Image.open(image_path) as img:
            img.thumbnail(max_size)
            resized_path = f"{os.path.splitext(image_path)[0]}_resized{os.path.splitext(image_path)[1]}"
            img.save(resized_path)
        return resized_path

    @staticmethod
    def upload_to_s3(file, bucket_name=None):
        """
        Upload image to S3 bucket
        """
        if bucket_name is None:
            bucket_name = current_app.config.get('S3_BUCKET')
        
        s3_client = boto3.client('s3')
        
        try:
            unique_filename = ImageUtils.generate_unique_filename(file.filename)
            s3_client.upload_fileobj(
                file, 
                bucket_name, 
                unique_filename,
                ExtraArgs={'ContentType': file.content_type}
            )
            return f"https://{bucket_name}.s3.amazonaws.com/{unique_filename}"
        except ClientError as e:
            current_app.logger.error(f"S3 Upload Error: {e}")
            return None