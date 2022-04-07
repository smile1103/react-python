from django.db import models


class CustomerFile(models.Model):
    customer_file = models.FileField(upload_to="customer_files/")
    date_created = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=50)

    def __str__(self):
        return self.customer_file.name