from django.db import models

# Create your models here.

class Achievement(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    desc = models.TextField()

    def __str__(self):
        return self.name
    
class Criteria(models.Model):
    id = models.IntegerField(primary_key=True)

    # relationships
    achievement = models.OneToOneField(Achievement, on_delete=models.CASCADE, related_name='criteria')

class ChildCriteria(models.Model):
    id = models.IntegerField(primary_key=True)
    desc = models.TextField()

    #relationships
    parent_criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE, related_name="children")

    def __str__(self):
        return self.desc