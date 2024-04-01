from celery import shared_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from fileshare.models import UserFiles,SharedFiles,DownloadFile
from youtransfer.celery import app

@app.task
def remove_userfile(id):
    """
    Saves latest image from Flickr
    """
    userfile=False
    try:
        userfile=UserFiles.objects.get(id=id)
    except Exception as e:
        print(e)
    if userfile:
        userfile.delete()
    logger.info(f"user file with id {id} is deleted ")
