from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
import os

listing_images = 'auctions/static/auctions/'

class User(AbstractUser):
    pass


class Category(models.Model):
    title = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.title}"

class ContactForm(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name

class Listing(models.Model):
    title = models.CharField(max_length=88)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categories")
    start_price = models.IntegerField()
    current_price = models.IntegerField(default=0)
    special = models.BooleanField(default=False)
    image = models.ImageField(upload_to=listing_images, blank=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    winner = models.IntegerField(default=1)
    # duration = models.DurationField(null=False,
    #                                          blank=False,
    #                                          default='00:01:00',
    #                                          verbose_name=('timeslot_duration'),
    #                                          help_text=('[Day] [hour:[minutes]] format')
    #                                         )

    # def timeslot_duration_HHmm(self):
    #     sec = self.timeslot_duration.total_seconds()
    #     return '%02d:%02d' % (int((sec/3600)%3600), int((sec/60)%60))

    def __str__(self):
        return f"""{self.title}\n
            desription: {self.description}\n
            category: {self.category}\n
            start: {self.start_price}\n
            current: {self.current_price}\n
            active: {self.active}
"""
    def get_absolute_url(self):
        return reverse('auctions:listing-detail', kwargs={'pk': self.pk})
		
    def filename(self):
        return os.path.basename(self.image.url)


class Comment(models.Model):
    text = models.TextField()
    created = models.DateTimeField(auto_now=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.text} ({self.created}) on {self.listing.title} by {self.author}"

    def get_absolute_url(self):
        return reverse('auctions:comment-detail', kwargs={'pk': self.pk})


class Watch(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"on {self.listing.title} by {self.user} [{ self.id }]"

class Bid(models.Model):
    price = models.IntegerField()
    created = models.DateTimeField(auto_now=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.price} on {self.listing.title} by {self.author} ({self.created})"

