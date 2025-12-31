from django.db import models
from django.contrib.auth import get_user_model
from .utils import generate_unique_slug

User = get_user_model()


class BlogProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="blog/profiles/", null=True, blank=True
    )
    social_links = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StatusUpdate(models.TextChoices):
    DRAFT = "DR", "Draft"
    PUBLISHED = "PB", "Published"
    ARCHIVED = "AR", "Archived"


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    status = models.CharField(
        max_length=2, choices=StatusUpdate.choices, default=StatusUpdate.DRAFT
    )
    author = models.ForeignKey(BlogProfile, on_delete=models.CASCADE)
    cover_image = models.ImageField(upload_to="blog/covers/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.slug

    class Meta:
        ordering = ["-created_at"]

    def is_published(self):
        return self.status == StatusUpdate.PUBLISHED

    def is_draft(self):
        return self.status == StatusUpdate.DRAFT

    def is_archived(self):
        return self.status == StatusUpdate.ARCHIVED

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self.title, self.slug, BlogPost)
        super().save(*args, **kwargs)


class PostLikes(models.Model):
    post_id = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="likes"
    )
    user_id = models.ForeignKey(BlogProfile, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post_id", "user_id")

    def __str__(self):
        return f"{self.user_id} liked {self.post_id}"


class Comment(models.Model):
    post_id = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="comments"
    )
    user_id = models.ForeignKey(BlogProfile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    parent_comment = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    def __str__(self):
        return f"Comment by {self.user_id} on {self.post_id}"

    class Meta:
        ordering = ["created_at"]


# class Tag(models.Model):
#     name = models.CharField(max_length=50, unique=True)
#     posts = models.ManyToManyField(BlogPost, related_name="tags")

#     def __str__(self):
#         return self.name

#     class Meta:
#         ordering = ["name"]


# class Category(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(blank=True)
#     posts = models.ManyToManyField(BlogPost, related_name="categories")

#     def __str__(self):
#         return self.name

#     class Meta:
#         ordering = ["name"]
