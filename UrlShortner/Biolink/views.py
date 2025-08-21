from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import BioLinkProfile as Profile, Link
from django.utils.text import slugify
from django.contrib import messages
from django.http import Http404
from django.db import transaction


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


def safe_get_or_create_profile(user):
    try:
        profile = Profile.objects.get(user=user)
        created = False
    except Profile.DoesNotExist:
        profile = Profile(user=user)
        profile.display_name = user.username
        base_slug = slugify(user.username)
        counter = 1
        unique_slug = base_slug
        while Profile.objects.filter(public_slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1

        profile.public_slug = unique_slug
        profile.save()
        created = True

    return profile, created


@login_required
@transaction.atomic
def editprofile(request):
    profile, created = safe_get_or_create_profile(user=request.user)
    if created:
        profile.display_name = request.user.username
        profile.public_slug = slugify(request.user.username)
        profile.save()
    if request.method == "POST":
        name = request.POST.get("display_name", "").strip()
        bio = request.POST.get("bio", "").strip()
        profile_image = request.FILES.get("profile_image")

        changes_made = False
        if name and name != profile.display_name:
            profile.display_name = name
            profile.public_slug = ""
            changes_made = True

        if bio != profile.bio:
            profile.bio = bio
            changes_made = True

        if profile_image:
            if profile.profile_image:
                profile.profile_image.delete(save=False)
            profile.profile_image = profile_image
            changes_made = True

        if changes_made:
            try:
                profile.save()
                messages.success(request, "Profile updated successfully!")
            except Exception as e:
                messages.error(request, f"Error updating profile: {str(e)}")
        else:
            messages.info(request, "No changes were made to your profile.")
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
