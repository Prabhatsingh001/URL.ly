from django.shortcuts import get_object_or_404, render

from .models import BlogPost


# Create your views here.
def blog_home(request):
    posts = BlogPost.objects.filter(status="PB").order_by("-published_at")
    return render(request, "blog_home.html", {"posts": posts})


def blog_post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status="DR")

    # Get related posts (same author, different post)
    related_posts = BlogPost.objects.filter(
        status="PB", author_id=post.author_id
    ).exclude(id=post.pk)[:3]

    context = {
        "post": post,
        "related_posts": related_posts,
    }

    return render(request, "blog_post_detail.html", context)
