from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.authentication import (
    TokenAuthentication, SessionAuthentication)


from .permissions import IsAuthorOrReadOnly, IsReviewTopicAuthorOrReadOnly
from .paginators import ReviewAPIListPaginator
from review.models import Review, ReviewTopic, Category
from .serializers import (
    ReviewSerializer, ReviewTopicSerializer,
    CategorySerializer
    )


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().prefetch_related('topics')
    serializer_class = ReviewSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'review_slug'
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    pagination_class = ReviewAPIListPaginator

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = (IsAuthenticatedOrReadOnly,)
        elif self.action == 'create':
            permission_classes = (IsAdminUser,)
        else:
            permission_classes = (IsAuthorOrReadOnly, IsAdminUser)
        return [permission() for permission in permission_classes]


class ReviewTopicDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReviewTopic.objects.all().select_related('review')
    serializer_class = ReviewTopicSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'topic_slug'
    permission_classes = (IsReviewTopicAuthorOrReadOnly, IsAdminUser)
    authentication_classes = (TokenAuthentication, SessionAuthentication)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'category_slug'
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = (IsAuthenticatedOrReadOnly,)
        else:
            permission_classes = (IsAdminUser,)
        return [permission() for permission in permission_classes]


class ReviewAPIView(APIView):
    def get(self, request):
        review_list = Review.objects.all()
        return Response(
            {'reviews': ReviewSerializer(review_list, many=True).data})

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"review": serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        slug = kwargs.get("review_slug", None)
        if not slug:
            return Response(
                {"error": "Method PUT not allowed"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
                )

        instance = get_object_or_404(Review, slug=slug)

        serializer = ReviewSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"review": serializer.data})

    def delete(self, request, *args, **kwargs):
        slug = kwargs.get("review_slug", None)
        if not slug:
            return Response(
                {"error": "Method DELETE not allowed"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
                )

        review = get_object_or_404(Review, slug=slug)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
