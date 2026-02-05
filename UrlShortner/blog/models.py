from django.db import models
from django.contrib.auth import get_user_model
from .utils import generate_unique_slug
from django.utils import timezone

User = get_user_model()


class BlogProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="blog/profiles/", null=True, blank=True
    )
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


class StatusUpdate(models.TextChoices):
    DRAFT = "DR", "Draft"
    PUBLISHED = "PB", "Published"
    ARCHIVED = "AR", "Archived"


class Blog(models.Model):
    author = models.ForeignKey(BlogProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    status = models.CharField(
        max_length=2, choices=StatusUpdate.choices, default=StatusUpdate.DRAFT
    )
    cover_image = models.ImageField(upload_to="blog/covers/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["published_at"]),
        ]

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self.title, self.slug, Blog)

        if self.status == StatusUpdate.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()

        if self.status == StatusUpdate.ARCHIVED and self.archived_at is None:
            self.archived_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def read_time(self):
        words = len(self.content.split())
        minutes = words // 200
        if minutes == 0:
            return "1 min read"
        return f"{minutes} min read"


class Comment(models.Model):
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    is_spam = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.post.title}"


class Like(models.Model):
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("post", "user")

    def __str__(self):
        return f"Like by {self.user.email} on {self.post.title}"
