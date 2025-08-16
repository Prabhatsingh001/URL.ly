from django.contrib.auth import get_user_model
from .models import UserProfile as Profile

User = get_user_model()


def save_profile(strategy, details, response, user=None, *args, **kwargs):
    if user is None:
        return

    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=user)

    # Fill fields from Google response
    if created or not profile.first_name:
        profile.first_name = details.get("fullname").split(" ")[0]

    if created or not profile.last_name:
        profile.last_name = details.get("fullname").split(" ")[1]

    # if created or not profile.profile_image:
    #     profile.profile_image = response.get("picture")

    profile.save()
