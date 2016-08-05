from django.db import models
from django.utils.encoding import python_2_unicode_compatible


class CSVDownload(models.Model):
    completed = models.BooleanField()
    filename = models.CharField(max_length=100)
    content = models.TextField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            u'CSVDownload(filename="{}", added={})'
            .format(self.filename, self.added)
        )
