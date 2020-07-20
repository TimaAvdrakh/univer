from django.db import models


class Instruction(models.Model):
    lang = [
        ('ru', 'Russian'),
        ('en', 'English'),
        ('kz', 'Kazakh')
    ]
    name = models.CharField(blank=False, max_length=200, unique=True)
    file = models.FileField(upload_to='instructions/', blank=True, null=True)
    language = models.CharField(choices=lang, max_length=2, null=False, blank=False)
    # uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.language}'
