from django.core.exceptions import ValidationError


def get_path_for_uploading_review_main_image(instance, file):
    """
    Returns a unique path for storing the main image of a review.
    """
    return f'review_main_images/{instance.title}/{file}'


def validate_image_size(file_obj):
    """
    Validates the size of an uploaded image file.
    """
    if file_obj.size > 1024 * 1024 * 5:  # 5MB limit
        raise ValidationError('Image size exceeds 5MB limit.')
