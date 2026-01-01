from django.db import models
from django.contrib.auth.models import User

class UserKeyPair(models.Model):
    # store users public key- private key stays in browser
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='keypair')
    public_key = models.TextField()
    encrypted_private_key = models.TextField()  # NEW: Encrypted with password-derived key
    salt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Chat(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_chats')
    #aes_key = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name if self.is_group else f"Private Chat {self.id}"

class ChatMember(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    encrypted_chat_key = models.TextField(null=True, blank=True)
    partner_public_key = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} in {self.chat.id}"
    
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    iv = models.TextField()