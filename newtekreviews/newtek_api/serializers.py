import io
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from review.models import Review, ReviewTopic, Category
from .utils import create_slug


# class ReviewSerializer(serializers.Serializer):
#     title = serializers.CharField(max_length=150)
#     slug = serializers.SlugField(max_length=255, read_only=True)
#     description = serializers.CharField()
#     main_image = serializers.ImageField(max_length=None, use_url=True, read_only=True)
#     time_created = serializers.DateTimeField(read_only=True)
#     time_updated = serializers.DateTimeField(read_only=True)
#     is_published = serializers.BooleanField(default=True)
#     author_id = serializers.IntegerField()
#     category_id = serializers.IntegerField()

#     def create(self, validated_data):
#         return Review.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         instance.title = validated_data.get('title', instance.title)
#         instance.description = validated_data.get('description', instance.description)
#         instance.main_image = validated_data.get('main_image', instance.main_image)
#         instance.time_updated = validated_data.get('time_updated', instance.time_updated)
#         instance.is_published = validated_data.get('is_published', instance.is_published)
#         instance.author_id = validated_data.get('author_id', instance.author_id)
#         instance.category_id = validated_data.get('category_id', instance.category_id)
#         instance.save()
#         return instance


class ReviewTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewTopic
        fields = [
            'review_topic_title', 'slug', 'text_content'
        ]
        read_only_fields = [
            'slug'
        ]


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    topics = ReviewTopicSerializer(many=True, required=False)

    class Meta:
        model = Review
        fields = [
            'title', 'slug', 'description', 'main_image', 'time_created',
            'time_updated',
            'is_published', 'author', 'category', 'topics'
        ]
        read_only_fields = [
            'slug', 'time_created', 'time_updated',
            'is_published', 'author', 'topics',
        ]

    def create(self, validated_data: dict):
        """
        Creates a new Review instance with validated data and related ReviewTopic instances.

        Parameters:
        - validated_data (dict): A dictionary containing the validated data for creating a new Review instance.
          It should include fields such as 'title', 'description', 'main_image', 'is_published', 'author',
          'category', and 'topics'. The 'topics' field should be a list of dictionaries, each containing
          'review_topic_title' and 'text_content'.

        Returns:
          Review: The newly created Review instance with associated ReviewTopic instances.
        """
        topics_data = validated_data.pop('topics')
        review = Review.objects.create(**validated_data)

        if topics_data:
            for topic_data in topics_data:
                slug = create_slug(review.title, topic_data['review_topic_title'])
                review_topic = ReviewTopic.objects.create(
                    review=review, slug=slug,
                    **topic_data)
                review_topic.save()
            review.save()

        return review

    def update(self, instance: Review, validated_data: dict):
        """
        Updates an existing Review instance with validated data and
        related ReviewTopic instances.

        Parameters:
        - instance (Review): The existing Review instance to be updated.
        - validated_data (dict): The validated data containing the updated
          fields for the Review instance.

        Returns:
          Review: The updated Review instance with associated ReviewTopic instances.
        """

        topics_data = validated_data.pop('topics')
        instance = super().update(instance, validated_data)

        associated_topics = {
            topic.slug: topic for topic in instance.topics.all()}
        updated_topic_slugs = []

        for topic_data in topics_data:
            topic_slug = topic_data.get('slug')
            if topic_slug and topic_slug in associated_topics:
                review_topic = associated_topics[topic_slug]
                review_topic.review_topic_title = topic_data['review_topic_title']
                review_topic.save()
                updated_topic_slugs.append(topic_slug)

            else:
                slug = create_slug(instance.title, topic_data['review_topic_title'])
                review_topic = ReviewTopic.objects.create(
                    review=instance, slug=slug, **topic_data)
                review_topic.save()
                updated_topic_slugs.append(review_topic.slug)

        # for topic_slug, topic in associated_topics.items():
        #     if topic_slug not in updated_topic_slugs:
        #         topic.delete()

        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'name', 'slug', 'category_background'
        ]
        read_only_fields = [
            'slug'
        ]
