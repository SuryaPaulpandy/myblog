import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyApp.settings')
django.setup()

from blog.models import Post, User

print(f"Total Posts: {Post.objects.count()}")
print(f"Posts with user=None: {Post.objects.filter(user__isnull=True).count()}")

users = User.objects.all()
for u in users:
    count = Post.objects.filter(user=u).count()
    print(f"User: '{u.username}' (ID: {u.id}) - Posts: {count}")
