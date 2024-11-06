from django.utils.text import slugify
from django.utils.crypto import get_random_string

from review.models import ReviewTopic


def create_slug(review_title, topic_title):
    base_slug = slugify(review_title + "-" + topic_title)
    slug = base_slug

    while ReviewTopic.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{get_random_string(6)}"

    return slug
