from django.db import models


from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class Message(models.Model):
    author = models.TextField()
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author

    def last_10_messages(self,room):
        return Message.objects.all().filter(author=room).order_by('timestamp')