from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Blog, StatusUpdate
from django.contrib.auth.decorators import login_required


@login_required()
def blog_home(request):
    blogs = Blog.objects.filter(author=request.user.blogprofile)
    return render(request, "blog/blog_home.html", {"blogs": blogs})


@login_required()
def create_blog_post(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        author_profile = request.user.blogprofile
        blog_post = Blog.objects.create(
            title=title,
            content=content,
            auhtor=author_profile,
        )
        blog_post.save()
        return redirect("blog:blog_home")
    return render(request, "blog/blog_post_detail.html")


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
