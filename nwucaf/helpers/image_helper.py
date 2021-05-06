from django.utils import timezone
from time import time

def get_upload_path(self, filename):
    path = f"images/{self._meta.model_name}/{timezone.localdate()}"
    filename = f"{int(time())}-{filename}"
    return f"{path}/{filename}"

def get_file_path(self, filename):
    path = f"firstaid/{self._meta.model_name}/{timezone.localdate()}"
    filename = f"{int(time())}-{filename}"
    return f"{path}/{filename}"
