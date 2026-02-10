
from django.db import models

class UploadRecord(models.Model):
    filename = models.CharField(max_length=255)
    summary_json = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.filename} - {self.timestamp}"
