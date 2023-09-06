from django.db import models

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(max_length= 200, unique=True)
    description = models.TextField(max_length=250,blank=True)
    categoty_image = models.ImageField(upload_to='photos/categoty',blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.category_name
