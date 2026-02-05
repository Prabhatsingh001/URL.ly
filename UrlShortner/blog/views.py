from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Blog, BlogProfile, Comment, Like, StatusUpdate

User = get_user_model()


def blog_list(request):
    """Public blog listing with search and sorting"""
    query = request.GET.get("q", "")
    sort = request.GET.get("sort", "recent")

    posts = Blog.objects.filter(status=StatusUpdate.PUBLISHED)

    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(content__icontains=query))

    if sort == "popular":
        posts = posts.annotate(like_count=Count("likes")).order_by(
            "-like_count", "-published_at"
        )
    else:
        posts = posts.order_by("-published_at")

    # Featured post (most liked recent post)
    featured_post = (
        Blog.objects.filter(status=StatusUpdate.PUBLISHED)
        .annotate(like_count=Count("likes"))
        .order_by("-like_count", "-published_at")
        .first()
    )

    paginator = Paginator(posts, 9)
    page = request.GET.get("page", 1)
    posts = paginator.get_page(page)

    return render(
        request,
        "blog/blog_list.html",
        {
            "posts": posts,
            "featured_post": featured_post if not query else None,
            "query": query,
            "sort": sort,
        },
    )


def author_profile(request, username):
    """Public author profile page"""
    user = get_object_or_404(User, username=username)
    author = get_object_or_404(BlogProfile, user=user)

    posts = Blog.objects.filter(author=author, status=StatusUpdate.PUBLISHED).order_by(
        "-published_at"
    )

    # Calculate total likes for this author
    total_likes = Like.objects.filter(post__author=author).count()

    paginator = Paginator(posts, 10)
    page = request.GET.get("page", 1)
    posts = paginator.get_page(page)

    return render(
        request,
        "blog/author_profile.html",
        {
            "author": author,
            "posts": posts,
            "total_likes": total_likes,
        },
    )


@login_required()
def blog_home(request):
    profile, created = BlogProfile.objects.get_or_create(user=request.user)
    blogs = Blog.objects.filter(author=profile).order_by("-updated_at")

    published_blogs = blogs.filter(status=StatusUpdate.PUBLISHED)
    draft_blogs = blogs.filter(status=StatusUpdate.DRAFT)
    archived_blogs = blogs.filter(status=StatusUpdate.ARCHIVED)

    # Calculate stats
    total_likes = Like.objects.filter(post__author=profile).count()
    total_comments = Comment.objects.filter(
        post__author=profile, is_approved=True
    ).count()

    # Get recent comments on user's posts
    recent_comments = (
        Comment.objects.filter(post__author=profile, is_approved=True)
        .select_related("user", "post")
        .order_by("-created_at")[:5]
    )

    return render(
        request,
        "blog/blog_home.html",
        {
            "published_blogs": published_blogs,
            "draft_blogs": draft_blogs,
            "archived_blogs": archived_blogs,
            "profile": profile,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "recent_comments": recent_comments,
        },
    )


@login_required()
def edit_profile(request):
    """Edit blog profile"""
    profile, created = BlogProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.bio = request.POST.get("bio", profile.bio)
        profile.website = request.POST.get("website", profile.website)

        if request.FILES.get("profile_picture"):
            profile.profile_picture = request.FILES.get("profile_picture")

        profile.save()
        return redirect("blog:blog_home")

    return render(request, "blog/edit_profile.html", {"profile": profile})


@login_required()
def create_blog_post(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        cover_image = request.FILES.get("cover_image")
        status = request.POST.get("status", StatusUpdate.DRAFT)
        author_profile = request.user.blogprofile

        # Validate status
        if status not in StatusUpdate.values:
            status = StatusUpdate.DRAFT

        Blog.objects.create(
            title=title,
            content=content,
            author=author_profile,
            cover_image=cover_image,
            status=status,
        )
        return redirect("blog:blog_home")
    return render(request, "blog/blog_post_form.html")


@login_required()
def edit_blog_post(request, slug):
    """Edit existing blog post"""
    post = get_object_or_404(Blog, slug=slug, author=request.user.blogprofile)

    if request.method == "POST":
        post.title = request.POST.get("title", post.title)
        post.content = request.POST.get("content", post.content)
        status = request.POST.get("status", post.status)

        if status in StatusUpdate.values:
            post.status = status

        if request.FILES.get("cover_image"):
            post.cover_image = request.FILES.get("cover_image")

        post.save()
        return redirect("blog:blog_home")

    return render(request, "blog/blog_post_form.html", {"post": post})


@login_required()
def delete_blog_post(request, slug):
    """Delete a blog post"""
    post = get_object_or_404(Blog, slug=slug, author=request.user.blogprofile)

    if request.method == "POST":
        post.delete()
        return redirect("blog:blog_home")

    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required()
def update_blog_status(request, slug):
    new_status = request.POST.get("status")
    if new_status not in StatusUpdate.values:
        return JsonResponse({"error": "Invalid status"}, status=400)
    try:
        blog_post = Blog.objects.get(slug=slug, author=request.user.blogprofile)
        blog_post.status = new_status
        blog_post.save()
        return JsonResponse(
            {
                "success": True,
                "status": blog_post.get_status_display(),  # type: ignore
            }
        )
    except Blog.DoesNotExist:
        return JsonResponse({"error": "Blog post not found"}, status=404)


def view_blog_post(request, slug):
    blog_post = get_object_or_404(Blog, slug=slug)
    related_posts = (
        Blog.objects.filter(status=StatusUpdate.PUBLISHED)
        .exclude(id=blog_post.pk)
        .order_by("?")[:3]
    )

    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = blog_post.likes.filter(user=request.user).exists()  # type: ignore

    return render(
        request,
        "blog/blog_post_detail.html",
        {
            "post": blog_post,
            "related_posts": related_posts,
            "user_has_liked": user_has_liked,
        },
    )


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Blog, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({"success": True, "liked": liked, "count": post.likes.count()})  # type: ignore


@login_required
@require_POST
def add_comment(request, post_id):
    """Add a comment to a blog post"""
    post = get_object_or_404(Blog, id=post_id, status=StatusUpdate.PUBLISHED)
    content = request.POST.get("content", "").strip()

    if not content:
        return JsonResponse({"error": "Comment cannot be empty"}, status=400)

    comment = Comment.objects.create(
        post=post,
        user=request.user,
        content=content,
    )

    return JsonResponse(
        {
            "success": True,
            "comment": {
                "id": comment.pk,
                "content": comment.content,
                "user": comment.user.get_full_name() or comment.user.username,
                "created_at": comment.created_at.strftime("%B %d, %Y"),
                "profile_picture": (
                    comment.user.blogprofile.profile_picture.url  # type: ignore
                    if hasattr(comment.user, "blogprofile")
                    and comment.user.blogprofile.profile_picture  # type: ignore
                    else None
                ),
            },
            "count": post.comments.filter(is_approved=True).count(),  # type: ignore
        }
    )


@login_required
@require_POST
def delete_comment(request, comment_id):
    """Delete a comment (only by comment author or post author)"""
    comment = get_object_or_404(Comment, id=comment_id)

    # Check permission
    if comment.user != request.user and comment.post.author.user != request.user:
        return JsonResponse({"error": "Permission denied"}, status=403)

    post = comment.post
    comment.delete()

    return JsonResponse(
        {
            "success": True,
            "count": post.comments.filter(is_approved=True).count(),  # type: ignore
        }
    )
