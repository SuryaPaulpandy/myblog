import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyApp.settings')
django.setup()

from blog.models import Post, User

try:
    target_user = User.objects.get(username='Surya2002')
    print(f"Found user: {target_user.username} (ID: {target_user.id})")
    
    # Assign all posts to this user
    count = Post.objects.all().update(user=target_user)
    print(f"Successfully assigned {count} posts to {target_user.username}")

except User.DoesNotExist:
    print("User 'Surya2002' not found!")
except Exception as e:
    print(f"Error: {e}")
