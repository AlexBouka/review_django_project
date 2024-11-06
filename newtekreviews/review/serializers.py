import io
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from .models import Review


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


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'title', 'slug', 'description', 'main_image', 'time_created',
            'time_updated',
            'is_published', 'author', 'category'
        ]
        read_only_fields = [
            'slug', 'time_created', 'time_updated',
            'is_published'
            ]
