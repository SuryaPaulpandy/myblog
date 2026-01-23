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
        """Return the image URL, handling both online URLs and uploaded files"""
        if not self.img_url:
            return "https://via.placeholder.com/800x400?text=No+Image"
        
        img_str = str(self.img_url)
        
        # If it's already an online URL (http/https), return as is
        if img_str.startswith(("http://", "https://")):
            return img_str
        
        # For uploaded files, return the full URL
        try:
            # In production (Render), use the media URL
            from django.conf import settings
            if hasattr(self.img_url, 'url'):
                return self.img_url.url
            else:
                # Fallback: construct URL manually
                return f"{settings.MEDIA_URL}{img_str}"
        except:
            # Final fallback
            return "https://via.placeholder.com/800x400?text=Image+Not+Found"

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
