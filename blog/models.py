"""Django Models Modules"""

import hashlib
import os
from django.contrib.auth.models import User
from django.conf import settings
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
    img_url = models.ImageField(max_length=500, null=True, blank=True, upload_to="posts/images")
    image_url_online = models.URLField(max_length=500, null=True, blank=True, help_text="Online image URL (if provided instead of file upload)")
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
        """Return the image URL, handling online URLs, uploaded files, and category-based defaults"""
        # Priority: 1. Online URL 2. Uploaded file (if exists) 3. Category-based unique image
        
        # Category-based image seeds (base seeds for each category)
        category_seeds = {
            "Technology": "tech",
            "Science": "science",
            "Art": "art",
            "Sports": "sports",
            "Food": "food",
        }
        
        # Priority 1: If online URL is provided, use it directly
        if self.image_url_online:
            return self.image_url_online
        
        # Priority 2: If file is uploaded AND exists on disk, use the uploaded file
        if self.img_url and hasattr(self.img_url, 'name') and self.img_url.name:
            try:
                # Check if the file actually exists on disk
                file_path = os.path.join(settings.MEDIA_ROOT, self.img_url.name)
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    # File exists and is not empty - use it
                    uploaded_url = self.img_url.url
                    
                    # If .url returns a full URL, return it directly
                    if uploaded_url.startswith(('http://', 'https://')):
                        return uploaded_url
                    
                    # For relative URLs, Django will handle serving them via MEDIA_URL
                    # Return the relative URL - it should work if media serving is configured
                    return uploaded_url
                # File doesn't exist or is empty, fall through to placeholder
            except (ValueError, AttributeError, OSError, Exception):
                # If anything fails, fall through to category-based placeholder
                pass
        
        # Priority 3: No image provided or file doesn't exist - use category-based unique placeholder
        # This ensures ALL posts always have an image
        if self.id and self.category:
            category_name = self.category.name
            base_seed = category_seeds.get(category_name, "default")
            # Create unique seed: category + post ID + title hash + content hash (first 4 chars)
            title_hash = hashlib.md5(self.title.encode()).hexdigest()[:8] if self.title else "00000000"
            content_hash = hashlib.md5(self.content.encode()).hexdigest()[:4] if self.content else "0000"
            unique_seed = f"{base_seed}_{self.id}_{title_hash}_{content_hash}"
            return f"https://picsum.photos/seed/{unique_seed}/800/600"
        elif self.category:
            # Post not saved yet
            category_name = self.category.name
            base_seed = category_seeds.get(category_name, "default")
            title_hash = hashlib.md5(self.title.encode()).hexdigest()[:8] if self.title else "00000000"
            content_hash = hashlib.md5(self.content.encode()).hexdigest()[:4] if self.content else "0000"
            unique_seed = f"{base_seed}_{title_hash}_{content_hash}"
            return f"https://picsum.photos/seed/{unique_seed}/800/600"
        else:
            # Final fallback
            return f"https://picsum.photos/seed/default_{self.id or 'new'}/800/600"

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
