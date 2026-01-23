"""Django Management Command to Fix Image URLs to Use Online URLs"""

from typing import Any
from django.core.management.base import BaseCommand
from blog.models import Post

# Online image URLs for posts
IMAGE_URLS = [
    "https://picsum.photos/seed/ai1/800/600",
    "https://picsum.photos/seed/climate1/800/600",
    "https://picsum.photos/seed/photo1/800/600",
    "https://picsum.photos/seed/quantum1/800/600",
    "https://picsum.photos/seed/nutrition1/800/600",
    "https://picsum.photos/seed/football1/800/600",
    "https://picsum.photos/seed/energy1/800/600",
    "https://picsum.photos/seed/digital1/800/600",
    "https://picsum.photos/seed/space1/800/600",
    "https://picsum.photos/seed/culinary1/800/600",
    "https://picsum.photos/seed/basketball1/800/600",
    "https://picsum.photos/seed/cyber1/800/600",
    "https://picsum.photos/seed/color1/800/600",
    "https://picsum.photos/seed/marine1/800/600",
    "https://picsum.photos/seed/street1/800/600",
    "https://picsum.photos/seed/tennis1/800/600",
    "https://picsum.photos/seed/5g1/800/600",
    "https://picsum.photos/seed/abstract1/800/600",
    "https://picsum.photos/seed/genetics1/800/600",
    "https://picsum.photos/seed/farm1/800/600",
    "https://picsum.photos/seed/swimming1/800/600",
    "https://picsum.photos/seed/vr1/800/600",
    "https://picsum.photos/seed/sculpture1/800/600",
    "https://picsum.photos/seed/climate2/800/600",
    "https://picsum.photos/seed/baking1/800/600",
    "https://picsum.photos/seed/cricket1/800/600",
    "https://picsum.photos/seed/iot1/800/600",
    "https://picsum.photos/seed/watercolor1/800/600",
    "https://picsum.photos/seed/astronomy1/800/600",
    "https://picsum.photos/seed/coffee1/800/600",
    "https://picsum.photos/seed/olympic1/800/600",
]


class Command(BaseCommand):
    """Command to fix image URLs to use online URLs instead of local files"""

    help = "Updates post images to use online URLs for Render deployment"

    def handle(self, *args: Any, **options):
        """Main handler"""
        posts = Post.objects.all().order_by('id')
        total = posts.count()
        
        self.stdout.write(f"Found {total} posts to update...")
        
        updated_count = 0
        for idx, post in enumerate(posts):
            # Check if image is already an online URL
            img_str = str(post.img_url) if post.img_url else ""
            
            if img_str.startswith(("http://", "https://")):
                self.stdout.write(f"  [SKIP] Post '{post.title[:50]}...' already has online URL")
                continue
            
            # Assign online URL
            if idx < len(IMAGE_URLS):
                online_url = IMAGE_URLS[idx]
            else:
                # Use a default placeholder
                online_url = f"https://picsum.photos/seed/{post.id}/800/600"
            
            # Update the post with online URL
            # We need to set it as a string, but ImageField expects a file
            # So we'll use a workaround - store URL in a way that formatted_img_url can handle
            try:
                # For ImageField, we can't directly set a URL string
                # Instead, we'll update the model to handle this better
                # For now, let's use a different approach - update via raw SQL or model field
                post.img_url = None  # Clear existing
                post.save()
                
                # Store URL in a way that can be retrieved
                # Since ImageField doesn't support URLs directly, we need to modify the approach
                # Actually, let's create a migration or use a CharField for URL storage
                # For quick fix, let's use the model's save method to handle this
                
                # Better approach: Use the ImageField's name attribute to store URL
                # But this won't work directly. Let's use a workaround.
                
                # Actually, the best solution is to update the database directly
                from django.db import connection
                with connection.cursor() as cursor:
                    # Update the img_url field to store the URL as a string
                    cursor.execute(
                        "UPDATE blog_post SET img_url = %s WHERE id = %s",
                        [online_url, post.id]
                    )
                
                updated_count += 1
                self.stdout.write(f"  [OK] Updated post '{post.title[:50]}...' with online URL")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  [ERROR] Failed to update '{post.title[:50]}...': {str(e)}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"\n[SUCCESS] Updated {updated_count} posts with online image URLs!")
        )
