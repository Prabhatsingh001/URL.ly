from django.utils.text import slugify


def generate_unique_slug(title, field_value, model_class):
    base_slug = slugify(title)
    slug = base_slug

    counter = 1
    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
