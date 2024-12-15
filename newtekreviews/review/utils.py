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

    def get_filter_headings(self, archived=False) -> str:
        """
        Returns a string that describes the current filter applied to the
        list view.

        If a page number is provided in the query string, the method returns
        a string of the form 'All reviews <page number> page' or 'Archived
        reviews <page number> page', depending on whether the view is showing
        archived or published reviews.

        If a title, description, or creation date is provided in the query
        string, the method returns a string describing the filter, for example
        'Reviews by title: <title>, description containing: <description>, and
        creation date: <date>'.

        If none of the above criteria are met, the method returns 'All Reviews'
        or 'Archived Reviews', depending on whether the view is showing
        archived or published reviews.

        :param archived: Whether the view is showing archived or published
            reviews
        :type archived: bool
        :return: A string that describes the current filter
        :rtype: str
        """
        filter_data = self.request.GET.dict()
        page = filter_data.get("page", '')
        title = filter_data.get("title", '')
        description = filter_data.get("description", '')
        time_created = filter_data.get("time_created", '')

        info_parts = []

        if page:
            return f'{'All reviews' if not archived else 'Archived reviews'} {page} page'
        if title:
            info_parts.append(f'title: {title}')
        if description:
            info_parts.append(f'description containing: {description}')
        if time_created:
            info_parts.append(f'creation date: {time_created}')

        list_type = 'Archived reviews by ' if archived else 'Reviews by '
        list_title = 'All Reviews' if not archived else 'Archived Reviews'

        return list_type + ", ".join(info_parts) \
            if info_parts else list_title


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
            and old.review_topic_title != new.review_topic_title:
        return slugify(
            f"{new.review.title}-{new.review_topic_title}")

    return old.slug
