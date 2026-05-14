from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    ITEM_TYPE = (
        ('lost', 'Lost'),
        ('found', 'Found'),
    )
    STATUS = (
        ('active', 'Active'),
        ('resolved', 'Resolved'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE)
    status = models.CharField(max_length=10, choices=STATUS, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.content[:40]}"
