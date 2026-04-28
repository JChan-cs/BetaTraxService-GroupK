from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Comment(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="The user who made the comment."
    )
    text = models.TextField(
        help_text="The content of the comment."
    )
    defect = models.ForeignKey('defects.DefectReport', on_delete=models.CASCADE, related_name='comments', null=True, help_text="The defect report this comment is associated with.")
    created_at = models.DateTimeField(
        default= timezone.now,
        help_text="The timestamp when the comment was created."
    )

    def __str__(self):
        return f"Comment by {self.author.username}"
