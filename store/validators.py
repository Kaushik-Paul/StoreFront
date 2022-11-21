from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger("storefront")


def validate_file_size(file):
    max_file_size = 50
    logger.info(f"FILE SIZE =========>>>>>>>>> {file.size}")
    if file.size > max_file_size:
        raise ValidationError(f"File size must be less than {max_file_size} KB")
