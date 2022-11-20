from time import sleep
from celery import shared_task
import logging

logger = logging.getLogger("storefront")


@shared_task
def send_notification_to_customer(message):
    logger.info(f"CELERY TASK IS RUNNING")
    logger.info(f"MESSAGE==========>>>>> {message}")
    sleep(10)
    logger.info(f"MESSAGE SENT")
