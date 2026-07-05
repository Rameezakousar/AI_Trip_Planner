from django.db import models
from django.contrib.auth.models import User

class Trip(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.IntegerField()
    travelers = models.IntegerField()
    hotel = models.CharField(max_length=100)
    transport = models.CharField(max_length=100)

    itinerary = models.TextField()

    image_url = models.URLField(blank=True)   # <-- THIS MUST EXIST
    favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.destination} ({self.user.username})"
