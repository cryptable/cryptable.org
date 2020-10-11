from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from blog.utils import get_random_string


class Article(models.Model):
    """
    The Article model to store the articles of the blog
    """
    title = models.CharField(max_length=100)
    summary = models.CharField(max_length=250)
    article = models.TextField()
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    slug = models.SlugField(unique=True)
    owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            tmp_slug = self.title + ' ' + get_random_string(8)
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)