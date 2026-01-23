"""Django Management Command to Fix User Permissions"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from blog.models import Post


class Command(BaseCommand):
    """Command to fix permissions for users"""

    help = "Fixes permissions for users - adds them to Editors group and assigns all blog permissions"

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to fix permissions for (default: Surya)',
            default='Surya'
        )

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"Fixing permissions for user: {user.username}")
            
            # Add to Editors group
            try:
                editors_group, created = Group.objects.get_or_create(name="Editors")
                user.groups.add(editors_group)
                self.stdout.write(self.style.SUCCESS(f"[OK] Added {user.username} to Editors group"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"[WARNING] Could not add to group: {str(e)}"))
            
            # Assign all blog permissions
            try:
                content_type = ContentType.objects.get_for_model(Post)
                permissions = Permission.objects.filter(content_type=content_type)
                for perm in permissions:
                    user.user_permissions.add(perm)
                self.stdout.write(self.style.SUCCESS(f"[OK] Assigned all blog permissions to {user.username}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"[WARNING] Could not assign permissions: {str(e)}"))
            
            # Ensure superuser status
            if not user.is_superuser:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f"[OK] Set {user.username} as superuser"))
            
            self.stdout.write(
                self.style.SUCCESS(f"\n[SUCCESS] Permissions fixed for {user.username}!")
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"[ERROR] User '{username}' not found!")
            )
