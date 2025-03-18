import os
import uuid
from PIL import Image
import numpy as np
import tensorflow as tf
from typing import Tuple, List
import base64

class ImageUtils:
    """
    Comprehensive Image Utility Class
    """
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """
        Generate a unique filename
        
        :param original_filename: Original filename
        :return: Unique filename
        """
        ext = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        return unique_filename

    @staticmethod
    def resize_image(image_path: str, max_size: Tuple[int, int] = (800, 800)) -> str:
        """
        Resize image while maintaining aspect ratio
        
        :param image_path: Path to the image
        :param max_size: Maximum dimensions
        :return: Path to resized image
        """
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.LANCZOS)
            
            # Generate new filename
            filename = ImageUtils.generate_unique_filename(os.path.basename(image_path))
            new_path = os.path.join(os.path.dirname(image_path), filename)
            
            img.save(new_path)
            return new_path

    @staticmethod
    def convert_to_base64(image_path: str) -> str:
        """
        Convert image to base64 string
        
        :param image_path: Path to the image
        :return: Base64 encoded image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    @staticmethod
    def load_image_tensor(image_path: str, target_size: Tuple[int, int] = (224, 224)) -> tf.Tensor:
        """
        Load and preprocess image for machine learning models
        
        :param image_path: Path to the image
        :param target_size: Target image dimensions
        :return: Preprocessed image tensor
        """
        img = tf.io.read_file(image_path)
        img = tf.image.decode_image(img, channels=3)
        img = tf.image.resize(img, target_size)
        img = img / 255.0  # Normalize pixel values
        img = tf.expand_dims(img, axis=0)  # Add batch dimension
        return img

    @staticmethod
    def detect_image_type(image_path: str) -> str:
        """
        Detect image type/format
        
        :param image_path: Path to the image
        :return: Image format
        """
        with Image.open(image_path) as img:
            return img.format.lower()

    @staticmethod
    def validate_image(image_path: str) -> bool:
        """
        Validate image file
        
        :param image_path: Path to the image
        :return: Boolean indicating valid image
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False