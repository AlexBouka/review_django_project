from django.urls import path
from django.views.decorators.cache import cache_page

from .views import (
    index, about, search_reviews,
    ReviewListView, ArchivedReviewListView,
    ReviewDetailView, ReviewCreateView, ReviewUpdateView, ReviewDeleteView,
    ReviewTopicCreateView, ReviewTopicUpdateView, ReviewTopicDeleteView,
    CategoryListView, CategoryDetailView, CategoryCreateView,
    CategoryUpdateView, CategoryDeleteView,
    ContactFormView,
    )


app_name = 'review'

urlpatterns = [
    path('', index, name='main'),
    path('about/', about, name='about'),
    path('contact/', ContactFormView.as_view(), name='contact'),
    path('search-results/', search_reviews, name='search'),

    # Review URLs
    path(
        'reviews/', ReviewListView.as_view(),
        name='all_reviews'
        ),
    path(
        'archived_reviews/', ArchivedReviewListView.as_view(),
        name='archived_reviews'
        ),
    path(
        'review/<slug:review_slug>/', ReviewDetailView.as_view(),
        name='review'
        ),
    path(
        'create/', ReviewCreateView.as_view(),
        name='review_create'
        ),
    path(
        'update/<slug:slug>/', ReviewUpdateView.as_view(),
        name='review_update'
        ),
    path(
        'delete/<slug:slug>/', ReviewDeleteView.as_view(),
        name='review_delete'
        ),

    # ReviewTopic URLs
    path(
        'create_topic/', ReviewTopicCreateView.as_view(),
        name='create_review_topic'
        ),
    path(
        'update_topic/<slug:topic_slug>/', ReviewTopicUpdateView.as_view(),
        name='update_review_topic'
        ),
    path(
        'delete_topic/<slug:topic_slug>/', ReviewTopicDeleteView.as_view(),
        name='delete_review_topic'
        ),

    # Category URLs
    path(
        'categories/', CategoryListView.as_view(),
        name='categories'
        ),
    path(
        'categories/<slug:category_slug>/', CategoryDetailView.as_view(),
        name='category'
        ),
    path(
        'create_category/', CategoryCreateView.as_view(),
        name='category_create'
        ),
    path(
        'update_category/<slug:category_slug>/', CategoryUpdateView.as_view(),
        name='category_update'
        ),
    path(
        'delete_category/<slug:category_slug>/', CategoryDeleteView.as_view(),
        name='category_delete'
        ),
]
