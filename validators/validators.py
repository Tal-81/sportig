"""
Utility validators for file uploads and form data.
"""

from django.core.exceptions import ValidationError
import os


ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
MAX_IMAGE_SIZE_MB = 5


def validate_image_file(file):
    """Validate uploaded image files."""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Unsupported file type: {ext}. '
            f'Allowed types: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}'
        )

    max_size = MAX_IMAGE_SIZE_MB * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(
            f'File size exceeds {MAX_IMAGE_SIZE_MB}MB limit.'
        )


def validate_positive_price(value):
    """Ensure price is positive."""
    if value <= 0:
        raise ValidationError('Price must be a positive number.')


def validate_stock_quantity(value):
    """Ensure stock is non-negative."""
    if value < 0:
        raise ValidationError('Stock quantity cannot be negative.')
