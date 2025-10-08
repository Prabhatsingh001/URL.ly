from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import BioLinkProfile as Profile, Link
from django.utils.text import slugify
from django.contrib import messages
from django.http import Http404
from django.db import transaction
import uuid


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
    biolink = get_object_or_404(Profile, user_id=id)
    links = biolink.links.all().order_by("-created_at")  # type: ignore
    context = {"links": links, "user": request.user}
    return render(request, "mainpage.html", context)


@login_required
def Addlink(request, id):
    if request.method == "POST":
        url = request.POST.get("url")
        title = request.POST.get("title")
        biolink = get_object_or_404(Profile, user_id=id)  # Get actual user object
        Link.objects.create(profile=biolink, title=title, url=url)
        return redirect("biolinkpage", id=request.user.id)
    return render(request, "mainpage.html")


@login_required()
def Deletelink(request, id):
    biolink = get_object_or_404(Profile, user=request.user)
    url = get_object_or_404(Link, id=id, profile=biolink)
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
def editprofile(request, id):
    profile, created = safe_get_or_create_profile(user=request.user)
    name_changed = request.session.get("name_changed", False)
    if request.method == "POST":
        name = request.POST.get("display_name", "").strip()
        bio = request.POST.get("bio", "").strip()
        profile_image = request.FILES.get("profile_image")

        changes_made = False
        if name and name != profile.display_name:
            profile.display_name = name
            changes_made = True
            request.session["name_changed"] = True

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
        return redirect("editprofile", id=request.user.id)
    return render(
        request, "mainpage.html", {"profile": profile, "name_changed": name_changed}
    )


@login_required
def enable_public_link(request):
    if request.method == "POST":
        profile = get_object_or_404(Profile, user=request.user)

        if profile.display_name:
            base_slug = slugify(profile.display_name)
        else:
            base_slug = slugify(profile.user.username)

        unique_slug = base_slug
        while (
            Profile.objects.filter(public_slug=unique_slug)
            .exclude(pk=profile.pk)
            .exists()
        ):
            unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

        profile.public_slug = unique_slug
        profile.save()

        request.session["name_changed"] = False

        messages.success(request, "Public link regenerated successfully!")
        return redirect("biolinkpage", id=request.user.id)

    return render(request, "mainpage.html")


def public_biolink_by_slug(request, slug):
    try:
        profile = Profile.objects.select_related("user").get(public_slug=slug)
    except Profile.DoesNotExist:
        raise Http404("Profile not found")
    except Profile.user.RelatedObjectDoesNotExist:
        raise Http404("User not found")
    links = Link.objects.filter(profile=profile, is_public=True)
    return render(
        request,
        "public_page.html",
        {
            "owner": profile.user,
            "profile": profile,
            "links": links,
        },
    )
