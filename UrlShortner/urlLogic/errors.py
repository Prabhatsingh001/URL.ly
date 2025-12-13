from django.shortcuts import render, redirect
from django.contrib import messages


def F404_page(request, excetipon):
    """
    Handle 404 Not Found errors with a custom template.

    Args:
        request: The HTTP request object
        excetipon: The exception that triggered the 404

    Returns:
        HttpResponse: Rendered 404 page with custom branding

    This view provides a user-friendly 404 page that maintains
    site branding and suggests next steps to users.
    """
    return render(request, "404_notF.html", status=404)


def F500_page(request):
    """
    Handle 500 Server Error responses with a custom template.

    Args:
        request: The HTTP request object

    Returns:
        HttpResponse: Rendered 500 page with custom branding

    Provides a user-friendly error page for server-side errors
    while maintaining site branding and suggesting next steps.
    """
    return render(request, "server_500.html", status=500)


def custom_403_view(request, exception=None):
    """
    Handle rate limit exceeded (403 Forbidden) responses.

    Args:
        request: The HTTP request object
        exception: Optional exception that triggered the 403

    Returns:
        HttpResponse: Redirect to index with error message

    Used primarily for rate limiting responses, providing user-friendly
    feedback when request limits are exceeded.
    """
    message = "You are sending requests too quickly. Please wait a few moments before trying again."
    messages.error(request, message)
    return redirect("index")
