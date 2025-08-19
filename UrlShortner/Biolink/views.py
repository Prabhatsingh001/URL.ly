from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import BioLinkProfile as Profile, Link
from django.utils.text import slugify
from django.contrib import messages
from django.http import Http404


User = get_user_model()

# Create your views here.


@login_required
def my_biolink_page(request):
    try:
        id = request.user.id
        return redirect("biolinkpage", id=id)
    except AttributeError as e:
        print(f"Error: {e}")
        messages.error(request, "User not found or not logged in.")
        return redirect("create_biolink")
    except Exception as e:
        print(f"Error: {e}")
        return redirect("u:home")


@login_required()
def Getlinks(request, id):
    links = Link.objects.filter(user_id=id).order_by("-created_at")
    context = {"links": links}
    return render(request, "mainpage.html", context)


@login_required
def Addlink(request, id):
    if request.method == "POST":
        url = request.POST.get("url")
        title = request.POST.get("title")
        user_instance = User.objects.get(id=id)  # Get actual user object
        Link.objects.create(user=user_instance, title=title, url=url)
        return redirect("biolinkpage", id=request.user.id)
    return render(request, "mainpage.html")


@login_required()
def Deletelink(request, id):
    url = get_object_or_404(Link, id=id, user=request.user)
    if request.method == "POST":
        url.delete()
    return redirect("biolinkpage", id=request.user.id)


@login_required
def editprofile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if not profile:
        profile = Profile.objects.create(user=request.user)
        profile.save()
    if request.method == "POST":
        name = request.POST.get("display_name")
        bio = request.POST.get("bio")
        profile_image = request.FILES.get("profile_image")

        if name and name != profile.display_name:
            profile.display_name = name
            profile.public_slug = ""

        if bio and bio != profile.bio:
            profile.bio = bio

        if profile_image:
            profile.profile_image = profile_image

        profile.save()
        return redirect("biolinkpage", id=request.user.id)

    return render(request, "mainpage.html")


@login_required
def enable_public_link(request):
    if request.method == "POST":
        profile = get_object_or_404(Profile, user=request.user)

        if not profile.display_name:
            profile.public_slug = slugify(profile.user.username)
        else:
            profile.public_slug = slugify(profile.display_name)

        profile.save()
        messages.success(request, "Public link generated successfully!")
        return redirect("biolinkpage", id=request.user.id)
    return render(request, "mainpage.html")


def public_biolink_by_slug(request, slug):
    try:
        profile = Profile.objects.select_related("user").get(public_slug=slug)
    except Profile.DoesNotExist:
        raise Http404("Profile not found")
    except Profile.user.RelatedObjectDoesNotExist:
        raise Http404("User not found")
    links = Link.objects.filter(user=profile.user, is_public=True)
    return render(
        request,
        "public_page.html",
        {
            "owner": profile.user,
            "profile": profile,
            "links": links,
        },
    )


def public_biolink_by_uuid(request, public_id):
    profile = get_object_or_404(Profile, public_id=public_id)
    links = Link.objects.filter(user=profile.user, is_public=True)
    return render(
        request,
        "public_page.html",
        {
            "owner": profile.user,
            "profile": profile,
            "links": links,
        },
    )
