"""Django Models Modules"""

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    """This is a post title"""

    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class Post(models.Model):
    """To all data in Post Model"""

    title = models.CharField(max_length=100)
    content = models.TextField()
    img_url = models.ImageField(max_length=500, null=True, upload_to="posts/images")
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # New Field for Saved/Bookmarked Posts
    saved_by = models.ManyToManyField(User, related_name='saved_posts', blank=True)

    is_published = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title)
            self.slug = slug[:500]  # truncate to avoid DB error
        super().save(*args, **kwargs)

    @property
    def formatted_img_url(self):
        url = (
            self.img_url
            if str(self.img_url).startswith(("http://", "https://"))
            else self.img_url.url
        )
        return url

    def __str__(self):
        return str(self.title)


class AboutUs(models.Model):
    """To get a aboutus"""

    content = models.TextField()


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
