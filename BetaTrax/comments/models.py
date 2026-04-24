from django.db import models
from django.contrib.auth.models import User

class Comment(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        help_text="The content of the comment."
    )
    defect = models.ForeignKey('defects.DefectReport', on_delete=models.CASCADE, related_name='comments', null=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The timestamp when the comment was created."
    )

    def __str__(self):
        return f"Comment by {self.author.username}"
