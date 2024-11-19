import django_filters

from .models import Review, Category


class ReviewFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    time_created = django_filters.DateFilter(lookup_expr='gt')

    class Meta:
        model = Review
        fields = ['title', 'description', 'time_created']


class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Category
        fields = ['name']
