from django.core.exceptions import ValidationError


def validate_file_size(value):
    """
    Validate that uploaded files don't exceed the size limit.

    Args:
        value: The uploaded file object to validate

    Raises:
        ValidationError: If file size exceeds 2 MiB

    This validator is used primarily for profile image uploads.
    """
    limit = 2 * 1024 * 1024  # 2 MB
    if value.size > limit:
        raise ValidationError("File too large. Size should not exceed 2 MiB.")
