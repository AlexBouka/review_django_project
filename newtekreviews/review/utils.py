from django.utils.text import slugify

from .models import Review, ReviewTopic


class DataMixin:
    page_title = None
    extra_context = {}

    def __init__(self) -> None:
        if self.page_title:
            self.extra_context["page_title"] = self.page_title

    def get_mixin_context(self, context, **kwargs):
        context["page_title"] = self.page_title
        context.update(kwargs)
        return context


def update_slug(old_instance, new_instance) -> str:
    if isinstance(old_instance, Review) and \
            old_instance.title != new_instance.title:
        return slugify(new_instance.title)
    elif isinstance(old_instance, ReviewTopic) \
            and old_instance.review_topic_title != new_instance.review_topic_title \
            or old_instance.review.title != new_instance.review.title:
        return slugify(
            f"{new_instance.review.title}-{new_instance.review_topic_title}")
