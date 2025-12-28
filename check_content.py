import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyApp.settings')
django.setup()

from blog.models import Post, User

try:
    user = User.objects.get(username='Surya2002')
    posts = Post.objects.filter(user=user)[:5] # Check first 5 posts
    for p in posts:
        print(f"Title: {p.title}")
        print(f"Content (raw): '{p.content}'")
        print("-" * 20)

except Exception as e:
    print(f"Error: {e}")
