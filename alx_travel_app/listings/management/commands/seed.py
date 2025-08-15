# listings/management/commands/seed.py

from django.core.management.base import BaseCommand
from listings.models import User, Listing
import random
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = 'Seed database with sample listings'

    def handle(self, *args, **kwargs):
        # Create a host user
        host = User.objects.create_user(username='hostuser', email='host@example.com', password='password', role='host')

        # Create sample listings
        for _ in range(10):
            Listing.objects.create(
                host=host,
                name=fake.company(),
                description=fake.text(),
                location=fake.city(),
                pricepernight=round(random.uniform(50, 500), 2),
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded listings"))


