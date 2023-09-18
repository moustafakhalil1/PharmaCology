from django.db import models

# Create your models here.
class process(models.Model):
    pic=models.ImageField()
    def __str__(self) -> str:
        return self.pic
class HandwritingPerception(models.Model):
    input_image = models.ImageField(upload_to='perceptions/')
    output_text = models.CharField(max_length=255)
    missing_characters_count = models.IntegerField()
    missing_characters_percentage = models.FloatField()

   