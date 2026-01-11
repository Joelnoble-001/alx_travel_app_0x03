from django.core.management.base import BaseCommand
from alx_travel_app.listings.models import Listing
from django.contrib.auth.models import User
import random

class Command(BaseCommand):
    help = "Seed the database with sample listings"

    def handle(self, *args, **kwargs):
        # Ensure at least one user exists
        user, created = User.objects.get_or_create(username='hostuser')
        if created:
            user.set_password('password123')
            user.save()

        # Sample data
        titles = ["Beach House", "Modern Apartment", "Cozy Cottage", "Mountain Cabin"]
        locations = ["Lagos", "Abuja", "Port Harcourt", "Calabar"]

        for i in range(10):  # create 10 listings
            listing = Listing.objects.create(
                title=random.choice(titles),
                description="A wonderful place to stay",
                price_per_night=random.randint(50, 300),
                location=random.choice(locations),
                host=user
            )
            self.stdout.write(self.style.SUCCESS(f'Created listing: {listing.title}'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
