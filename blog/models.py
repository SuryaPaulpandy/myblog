"""Django Models Modules"""

import hashlib
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
        # Category-based image seeds (base seeds for each category)
        category_seeds = {
            "Technology": "tech",
            "Science": "science",
            "Art": "art",
            "Sports": "sports",
            "Food": "food",
        }
        
        if not self.img_url:
            # No image uploaded - generate unique image based on post details
            # Use combination of: category + post ID + title hash for uniqueness
            if self.id and self.category:
                category_name = self.category.name
                base_seed = category_seeds.get(category_name, "default")
                
                # Create unique seed from post ID, title, and category
                # This ensures no two posts get the same image
                title_hash = hashlib.md5(self.title.encode()).hexdigest()[:8] if self.title else "00000000"
                unique_seed = f"{base_seed}_{self.id}_{title_hash}"
                
                return f"https://picsum.photos/seed/{unique_seed}/800/600"
            elif self.category:
                # Post not saved yet, use category + title hash
                category_name = self.category.name
                base_seed = category_seeds.get(category_name, "default")
                title_hash = hashlib.md5(self.title.encode()).hexdigest()[:8] if self.title else "00000000"
                unique_seed = f"{base_seed}_{title_hash}"
                return f"https://picsum.photos/seed/{unique_seed}/800/600"
            else:
                # Fallback
                return f"https://picsum.photos/seed/default_{self.id or 'new'}/800/600"
        
        img_str = str(self.img_url)
        
        # If it's already an online URL (http/https), return as is
        if img_str.startswith(("http://", "https://")):
            return img_str
        
        # For uploaded files, try to construct the URL
        try:
            from django.conf import settings
            import os
            
            # Get file path
            if hasattr(self.img_url, 'name'):
                file_path = self.img_url.name
            elif hasattr(self.img_url, 'url'):
                try:
                    url = self.img_url.url
                    if url.startswith(('http://', 'https://')):
                        return url
                    # Construct absolute URL for production
                    if not settings.DEBUG:
                        try:
                            from django.contrib.sites.models import Site
                            current_site = Site.objects.get_current()
                            domain = current_site.domain
                            if not domain.startswith('http'):
                                domain = f"https://{domain}"
                            return f"{domain}{url}"
                        except:
                            pass
                    return url
                except:
                    file_path = img_str
            else:
                file_path = img_str
            
            # Remove leading slash
            if file_path.startswith('/'):
                file_path = file_path[1:]
            
            # Check if file exists locally
            full_path = os.path.join(settings.MEDIA_ROOT, file_path) if hasattr(settings, 'MEDIA_ROOT') else None
            file_exists = full_path and os.path.exists(full_path) if full_path else False
            
            # Construct URL
            media_url = settings.MEDIA_URL
            if not media_url.endswith('/'):
                media_url += '/'
            
            if file_exists and settings.DEBUG:
                # File exists in development
                return f"{media_url}{file_path}"
            elif not settings.DEBUG:
                # In production (Render), try absolute URL
                try:
                    from django.contrib.sites.models import Site
                    current_site = Site.objects.get_current()
                    domain = current_site.domain
                    if not domain.startswith('http'):
                        domain = f"https://{domain}"
                    return f"{domain}{media_url}{file_path}"
                except:
                    # Fallback: use unique category-based image
                    if self.id and self.category:
                        category_name = self.category.name
                        base_seed = category_seeds.get(category_name, "default")
                        title_hash = hashlib.md5(self.title.encode()).hexdigest()[:8] if self.title else "00000000"
                        unique_seed = f"{base_seed}_{self.id}_{title_hash}"
                        return f"https://picsum.photos/seed/{unique_seed}/800/600"
                    return f"https://picsum.photos/seed/default_{self.id or 'new'}/800/600"
            else:
                # File doesn't exist, use unique category-based image
                if self.id and self.category:
                    category_name = self.category.name
                    base_seed = category_seeds.get(category_name, "default")
                    title_hash = hashlib.md5(self.title.encode()).hexdigest()[:8] if self.title else "00000000"
                    unique_seed = f"{base_seed}_{self.id}_{title_hash}"
                    return f"https://picsum.photos/seed/{unique_seed}/800/600"
                return f"https://picsum.photos/seed/default_{self.id or 'new'}/800/600"
                
        except Exception as e:
            # Final fallback - use unique category-based image
            if self.id and self.category:
                category_name = self.category.name
                base_seed = category_seeds.get(category_name, "default")
                title_hash = hashlib.md5(self.title.encode()).hexdigest()[:8] if self.title else "00000000"
                unique_seed = f"{base_seed}_{self.id}_{title_hash}"
                return f"https://picsum.photos/seed/{unique_seed}/800/600"
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
