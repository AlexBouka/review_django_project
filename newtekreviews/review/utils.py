from django.utils.text import slugify

from .models import Review, ReviewTopic


class DataMixin:
    page_title = None
    info_heading = None
    extra_context = {}

    def __init__(self) -> None:
        if self.page_title:
            self.extra_context["page_title"] = self.page_title

        if self.info_heading:
            self.extra_context["info_heading"] = self.info_heading

    def get_mixin_context(self, context, **kwargs):
        """
        Updates the given context dictionary with mixin-specific data.

        This method adds the `page_title` and `info_heading` attributes to the
        provided context dictionary and updates it with any additional keyword
        arguments.

        Parameters:
        - context (dict): The context dictionary to be updated.
        - **kwargs: Additional keyword arguments to be added to the context.

        Returns:
        dict: The updated context dictionary.
        """

        context["page_title"] = self.page_title
        context["info_heading"] = self.info_heading
        context.update(kwargs)
        return context


def update_slug(old, new) -> str:
    """
    Updates the slug of a Review or ReviewTopic instance if needed.

    This function checks if the title of the given `old` and `new` instances
    of either the `Review` or `ReviewTopic` class has changed. If the title
    of the `Review` instance or the `review_topic_title` of the `ReviewTopic`
    instance has changed, it generates a new slug using the updated title(s).

    Args:
        old: The original instance of either `Review` or `ReviewTopic`.
        new: The updated instance of either `Review` or `ReviewTopic`.

    Returns:
        str: A new slug generated from the updated title(s), if a change is detected.
    """

    if isinstance(old, Review) and \
            old.title != new.title:
        return slugify(new.title)
    elif isinstance(old, ReviewTopic) \
            and old.review_topic_title != new.review_topic_title \
            or old.review.title != new.review.title:
        return slugify(
            f"{new.review.title}-{new.review_topic_title}")
