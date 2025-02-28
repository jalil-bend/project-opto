from django.core.management.base import BaseCommand
from users.models import User, Professional

class Command(BaseCommand):
    help = 'Create Professional objects for existing professional users'

    def handle(self, *args, **kwargs):
        professional_users = User.objects.filter(is_professional=True)
        created_count = 0

        for user in professional_users:
            if not hasattr(user, 'professional'):
                Professional.objects.create(user=user)
                created_count += 1
                self.stdout.write(f"Created Professional object for {user.username}")

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} Professional objects"))
