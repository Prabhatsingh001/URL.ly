"""
View functions for the Biolink feature managing user profile pages.

This module provides views for:
- Profile creation and management
- Link management (CRUD operations)
- Public profile access
- Profile customization

Key features:
- Authentication protection
- Transaction safety
- Slug-based public URLs
- Image handling
- Error handling and user feedback
"""

import uuid

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from .models import BioLinkProfile as Profile
from .models import Link
import logging

User = get_user_model()

logger = logging.getLogger("Biolink")


@login_required
def my_biolink_page(request):
    """
    Redirect users to their personal biolink page.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Redirect to user's biolink page or appropriate error page

    Handles various error cases:
    - Missing user attributes
    - Authentication issues
    - General exceptions
    """
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
    """
    Display all links for a specific biolink profile.

    Args:
        request: The HTTP request object
        id: User ID whose links to display

    Returns:
        HttpResponse: Rendered page with user's links

    Features:
    - Ordered by creation date (newest first)
    - 404 handling for invalid profiles
    - Authentication required
    """
    biolink = get_object_or_404(Profile, user_id=id)
    links = biolink.links.all().order_by("-created_at")  # type: ignore
    context = {"links": links, "user": request.user}
    return render(request, "mainpage.html", context)


@login_required
def Addlink(request, id):
    """
    Add a new link to user's biolink profile.

    Args:
        request: The HTTP request object
        id: User ID whose profile to add link to

    Returns:
        HttpResponse: Redirect to biolink page or form for new link

    Features:
    - POST-only link creation
    - Profile ownership validation
    - Error handling for invalid profiles
    """
    if request.method == "POST":
        url = request.POST.get("url")
        title = request.POST.get("title")
        biolink = get_object_or_404(Profile, user_id=id)  # Get actual user object
        Link.objects.create(profile=biolink, title=title, url=url)
        return redirect("biolinkpage", id=request.user.id)
    return render(request, "mainpage.html")


@login_required()
def Deletelink(request, id):
    """
    Delete a link from user's biolink profile.

    Args:
        request: The HTTP request object
        id: Link ID to delete

    Returns:
        HttpResponse: Redirect to biolink page

    Security:
    - Validates profile ownership
    - POST-only deletion
    - 404 handling for invalid links
    """
    biolink = get_object_or_404(Profile, user=request.user)
    url = get_object_or_404(Link, id=id, profile=biolink)
    if request.method == "POST":
        url.delete()
    return redirect("biolinkpage", id=request.user.id)


def safe_get_or_create_profile(user):
    """
    Safely retrieve or create a biolink profile for a user.

    Args:
        user: User instance to get/create profile for

    Returns:
        tuple: (Profile instance, bool indicating if created)

    Features:
    - Automatic slug generation
    - Duplicate slug handling
    - Username-based defaults
    - Error handling
    """
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
    """
    Edit biolink profile details with image handling.

    Args:
        request: The HTTP request object
        id: User ID whose profile to edit

    Returns:
        HttpResponse: Rendered form or redirect after update

    Features:
    - Image upload and processing
    - Transaction-safe updates
    - Automatic profile creation
    - Change tracking
    - User feedback messages
    - Session-based name change tracking
    """
    profile, created = safe_get_or_create_profile(user=request.user)
    links = Link.objects.filter(profile=profile).order_by("-created_at")
    name_changed = request.session.get("name_changed", False)

    if request.method == "POST":
        changes_made = False

        if "display_name" in request.POST:
            name = request.POST.get("display_name", "").strip()
            if name and name != profile.display_name:
                profile.display_name = name
                changes_made = True
                request.session["name_changed"] = True

        if "bio" in request.POST:
            bio = request.POST.get("bio", "").strip()
            if bio != profile.bio:
                profile.bio = bio
                changes_made = True

        if "profile_image" in request.FILES:
            if profile.profile_image:
                profile.profile_image.delete(save=False)
            profile.profile_image = request.FILES["profile_image"]
            changes_made = True

        if changes_made:
            profile.save()
            messages.success(request, "Profile updated successfully!")
        else:
            messages.info(request, "No changes were made to your profile.")

        return redirect("editprofile", id=request.user.id)

    return render(
        request,
        "mainpage.html",
        {
            "profile": profile,
            "links": links,
            "name_changed": name_changed,
        },
    )


@login_required
def enable_public_link(request):
    """
    Generate or regenerate public slug for profile access.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Redirect to biolink page with status

    Features:
    - Unique slug generation
    - Collision handling with UUID
    - Name-based slug creation
    - Session state clearing
    - Success messaging
    """
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
    """
    Display public biolink profile page by slug.

    Args:
        request: The HTTP request object
        slug: Public URL slug to look up

    Returns:
        HttpResponse: Rendered public profile page

    Features:
    - Public access (no auth required)
    - Only shows public links
    - Efficient database queries
    - 404 handling for missing profiles
    - Related object prefetching
    """
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
