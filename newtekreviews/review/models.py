from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.urls import reverse

from .services import (
    validate_image_size, get_path_for_uploading_review_main_image)


class PublishedManager(models.Manager):
    def get_queryset(self):
        """
        This method overrides the `get_queryset` method of the parent class to filter the queryset
        to only include reviews that are published. It does this by calling the `get_queryset` method
        of the parent class and then filtering the resulting queryset to only include reviews with
        `is_published` equal to `Review.Status.PUBLISHED`.

        Returns:
            QuerySet: A queryset of published reviews.
        """

        return super().get_queryset().filter(
            is_published=Review.Status.PUBLISHED)


class ArchivedManager(models.Manager):
    def get_queryset(self):
        """
        This method overrides the `get_queryset` method of the parent class
        to filter the queryset to only include reviews that are archived.
        It does this by calling the `get_queryset` method
        of the parent class and then filtering the resulting queryset to only
        include reviews with `is_published` equal to `Review.Status.ARCHIVED`.

        Returns:
        QuerySet: A queryset of archived reviews.
        """

        return super().get_queryset().filter(
            is_published=Review.Status.DRAFT)


class Review(models.Model):
    """
    A model representing a review.

    Attributes:
        title (str): The title of the review.
        slug (str): A unique slug for the review, generated from the title.
        description (str): The description of the review.
        main_image (ImageField): The main image associated with the review.
        time_created (DateTimeField): The date and time the review was created.
        time_updated (DateTimeField): The date and time the review was last updated.
        is_published (BooleanField): Whether the review is published or not.
        author (ForeignKey): The user who wrote the review.
        category (ForeignKey): The category the review belongs to.

    Status:
        DRAFT (0): The review is a draft.
        PUBLISHED (1): The review is published.

    Managers:
        objects: A manager for all reviews.
        published: A manager for published reviews.
        archived: A manager for archived reviews.

    Methods:
        __str__: Returns the title of the review as a string representation.
        save: Saves the review instance, generating a unique slug if not already set.
        get_absolute_url: Returns the absolute URL of the review.
    """
    class Status(models.IntegerChoices):
        DRAFT = 0, "Draft"
        PUBLISHED = 1, "Published"

    title = models.CharField(
        max_length=150, db_index=True, verbose_name="Review Title")
    slug = models.SlugField(
        max_length=255, unique=True, db_index=True,
        validators=[
            MinLengthValidator(
                5, message="Slug must be at least 5 characters long"),
            MaxLengthValidator(
                100, message="Slug must be at most 100 characters long"),
            ]
        )
    description = models.TextField(
        verbose_name="Review Description", blank=True
    )
    main_image = models.ImageField(
        upload_to=get_path_for_uploading_review_main_image, default=None,
        blank=True, null=True,
        verbose_name="Main Image",
        validators=[
            validate_image_size
        ]
    )
    time_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Created")
    time_updated = models.DateTimeField(
        auto_now=True, verbose_name="Updated")
    is_published = models.BooleanField(
        choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
        default=True, verbose_name="Status")

    author = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL,
        related_name='reviews', null=True, default=None)

    category = models.ForeignKey(
        'Category', on_delete=models.CASCADE,
        related_name='reviews', null=True, blank=True
        )
    likes = models.ManyToManyField(
        get_user_model(), blank=True, related_name='liked_reviews')

    objects = models.Manager()  # Review.objects.all()
    published = PublishedManager()  # Review.published.all()
    archived = ArchivedManager()  # Review.archived.all()

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-time_created"]

    def __str__(self) -> str:
        return self.title

    def total_likes(self):
        """
        Calculates the total number of likes for this review.

        Returns:
            int: The number of likes associated with this review.
        """
        return self.likes.count()

    def save(self, *args, **kwargs):
        """
        Saves the Review instance.
        If the slug is not set, it generates a unique slug
        based on the review's title.
        It appends a random string to the base
        slug if a slug collision is detected, ensuring uniqueness.
        """
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug

            while Review.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{get_random_string(6)}"

            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('review:review', kwargs={'review_slug': self.slug})


class ReviewTopic(models.Model):
    """
    Represents a topic within a review.

    Attributes:
        review (ForeignKey): The parent review that this topic belongs to.
        review_topic_title (CharField): The title of the topic.
        slug (SlugField): A unique slug for the topic.
        text_content (TextField): The content of the topic.

    Methods:
        __str__: Returns the topic title as a string representation of the object.
        get_parent_review_title: Returns the title of the parent review
            that this topic belongs to.
        save: Saves the topic instance,
            generating a unique slug if not already set,
            and ensuring uniqueness by
            appending a random string if a slug collision is detected.
        get_absolute_url: Returns the absolute URL of the topic.
    """
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='topics', null=True, blank=True
        )

    review_topic_title = models.CharField(
        max_length=200, db_index=True, verbose_name="Topic Title")
    slug = models.SlugField(
        max_length=255, unique=True, db_index=True,
        validators=[
            MinLengthValidator(
                3, message="Slug must be at least 3 characters long"),
            MaxLengthValidator(
                200, message="Slug must be at most 200 characters long"),
            ]
        )
    text_content = models.TextField(
        verbose_name="Topic Content", blank=True
        )

    class Meta:
        verbose_name = "Topic"
        verbose_name_plural = "Topics"

    def __str__(self):
        return self.review_topic_title

    def get_parent_review_title(self):
        """Returns the title of the parent Review
        to which this topic belongs."""

        return self.review.title

    def save(self, *args, **kwargs):
        """
        Saves the ReviewTopic instance. If the slug is not set, it generates a unique
        slug based on the review's title and the topic's title. It appends a random
        string to the base slug if a slug collision is detected, ensuring uniqueness.
        """
        if not self.slug:
            base_slug = slugify(f"{self.review.title}-{self.review_topic_title}")
            slug = base_slug

            while ReviewTopic.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{get_random_string(6)}"

            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('review:topic', kwargs={'topic_slug': self.slug})


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments', null=True, blank=True
        )
    author = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='comments',
        null=True, blank=True)
    text = models.TextField(verbose_name="Comment")
    time_created = models.DateTimeField(auto_now_add=True)


class Category(models.Model):
    name = models.CharField(
        max_length=100, db_index=True, verbose_name="Category Title")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    category_background = models.ImageField(
        upload_to='category_background_images/', default=None,
        blank=True, null=True,
        verbose_name="Background"
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('review:category', kwargs={'category_slug': self.slug})
