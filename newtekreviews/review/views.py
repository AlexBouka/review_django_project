import logging

from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    View, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
    )
from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin
    )
from django.core.cache import cache

from .utils import DataMixin, update_slug
from .models import Review, ReviewTopic, Category
from .forms import (
    AddReviewForm, ContactForm, AddCategoryForm,
    AddReviewTopicForm, EditReviewTopicForm,
    ReviewTopicFormSet, UpdateReviewTopicFormSet)
from .filters import ReviewFilter, CategoryFilter

logger = logging.getLogger(__name__)


def index(request):
    return render(
        request, 'review/index.html'
        )


def about(request):
    return render(
        request, 'review/about.html'
        )


def contact(request):
    return render(
        request, 'review/contact.html'
        )


def search_reviews(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        reviews = Review.published.filter(title__icontains=searched)
        return render(
            request, 'review/search_reviews.html',
            {'searched': searched, 'reviews': reviews}
            )
    else:
        return render(
            request, 'review/search_reviews.html', {}
            )


class ReviewListView(DataMixin, ListView):
    model = Review
    page_title = 'All Reviews'
    info_heading = 'Reviews'
    context_object_name = 'reviews'
    template_name = 'review/review_list.html'
    paginate_by = 5

    def get_queryset(self):
        """
        Retrieves all published reviews from the cache or database.

        If the reviews are not in the cache, it retrieves all published reviews
        from the database and caches them.

        The reviews are filtered using the ReviewFilter class, which filters
        the reviews based on the GET parameters passed in the request.

        Returns:
            QuerySet: A queryset of all published reviews filtered by the GET
            parameters.
        """

        review_list = cache.get('all_reviews')
        if not review_list:
            review_list = Review.published.all().select_related(
                'category').select_related(
                    'author')
            cache.set('all_reviews', review_list, 60)

        self.filterset = ReviewFilter(self.request.GET, queryset=review_list)

        logger.info('Retrieving all reviews that are published...')

        return self.filterset.qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Retrieves the context data needed to render the review list page.

        The context includes the count of all published reviews, the count of
        filtered reviews, the ReviewFilter instance, and the filtered data.

        If the request contains GET parameters, it updates the info_heading
        attribute of the view instance with the appropriate text.

        Returns:
            dict[str, Any]: The context data needed to render the review list page.
        """
        context = super().get_context_data(**kwargs)
        context['reviews_count'] = Review.published.count()
        context['filtered_reviews_count'] = len(self.filterset.qs)
        context['filter'] = self.filterset

        filter_data = self.request.GET.dict()
        context['filter_data'] = filter_data

        info_parts = []

        if filter_data:
            logger.info(f'Retrieving filtered reviews: {filter_data}')

            page = filter_data.get('page')
            title = filter_data.get('title', '')
            description = filter_data.get('description', '')
            time_created = filter_data.get('time_created', '')

            if page:
                self.info_heading = f'All reviews {page} page'
            if title:
                info_parts.append(f"title: {title}")
            if description:
                info_parts.append(f"description containing: {description}")
            if time_created:
                info_parts.append(f"creation date: {time_created}")

        self.info_heading = 'Reviews by ' + ", ".join(info_parts) \
            if info_parts else "All Reviews"
        context['info_heading'] = self.info_heading

        return context


# Review CRUD views

class ReviewDetailView(DataMixin, DetailView):
    model = Review
    template_name = 'review/review_detail.html'
    slug_url_kwarg = 'review_slug'
    context_object_name = 'review'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(
            context, page_title="NewTekReviews - " + context['review'].title)

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        logger.info(
            f'Retrieving review: {get_object_or_404(
                Review, slug=self.kwargs[self.slug_url_kwarg]).title}'
            )
        return get_object_or_404(
            Review.published.select_related('author')
            .select_related('category'),
            slug=self.kwargs[self.slug_url_kwarg])


class ReviewCreateView(
        PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    form_class = AddReviewForm
    template_name = 'review/review_create.html'
    permission_required = ('review.add_review',)
    success_url = reverse_lazy('review:all_reviews')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['review_topic_formset'] = ReviewTopicFormSet(
                self.request.POST, queryset=ReviewTopic.objects.none())
        else:
            data['review_topic_formset'] = ReviewTopicFormSet(
                queryset=ReviewTopic.objects.none())
        return data

    def form_valid(self, form):
        """
        Validates and processes the main form
        and the associated review topic formset.

        This method first retrieves context data,
        including the `review_topic_formset`,
        and checks if both the main form and the formset are valid. If valid:

        - Saves the main form as a `review` instance
        without committing to the database initially.
        - Sets the `review.author` attribute to the currently logged-in user
        (`self.request.user`).
        - Finalizes saving the main form to create the `self.object`.

        For each valid form in `review_topic_formset`:
            - Initializes a `review_topic` instance
            without saving to the database.
            - Links `review_topic` to the main `review` object (`self.object`).
            - Saves each `review_topic` instance.

        Redirects to `self.success_url` upon successful form processing,
        otherwise calls `self.form_invalid(form)` if any form validation fails.

        Args:
            form: The main form instance for the review object.

        Returns:
            A redirect response to `self.success_url`
            if both the main form and formset
            are valid, or a call to `self.form_invalid(form)`
            if validation fails.
        """
        context = self.get_context_data()
        review_topic_formset = context['review_topic_formset']

        if form.is_valid() and review_topic_formset.is_valid():
            review = form.save(commit=False)
            review.author = self.request.user
            self.object = form.save()

            for review_topic_form in review_topic_formset:
                if review_topic_form.cleaned_data:
                    review_topic = review_topic_form.save(commit=False)
                    review_topic.review = self.object
                    review_topic.save()

            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class ReviewUpdateView(
        PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Review
    form_class = AddReviewForm
    template_name = 'review/review_update.html'
    permission_required = ('review.change_review',)
    success_url = reverse_lazy('review:all_reviews')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['review_topic_formset'] = UpdateReviewTopicFormSet(
                self.request.POST, self.request.FILES,
                queryset=ReviewTopic.objects.filter(review=self.object))
        else:
            data['review_topic_formset'] = UpdateReviewTopicFormSet(
                queryset=ReviewTopic.objects.filter(review=self.object))
        return data

    def form_valid(self, form):
        """
        Validates and processes the main form
        and the associated review topic formset.

        This method first retrieves the additional context data for the view,
        including the review topic formset. It checks if both the main form
        and the formset are valid. If they are:

        - The main form is saved to create or update a `review` instance.
        - Each form in the review topic formset is processed:
            - If marked for deletion (`DELETE` field), the instance is deleted.
            - If not marked for deletion and contains data, the review topic
            instance is saved and linked to the review.

        Redirects to `self.success_url` on success,
        otherwise returns an invalid form.

        Args:
            form: The main form for the review instance.

        Returns:
            A redirect response to `self.success_url` if both forms are valid,
            or a call to `self.form_invalid(form)` if either form is invalid.
        """
        context = self.get_context_data()
        review_topic_formset = context['review_topic_formset']

        if form.is_valid() and review_topic_formset.is_valid():
            review = form.save(commit=False)
            review.slug = update_slug(
                get_object_or_404(Review, slug=review.slug), form.instance)
            review.save()

            for review_topic_form in review_topic_formset:
                if review_topic_form.cleaned_data.get('DELETE', False):
                    review_topic_form.instance.delete()
                elif review_topic_form.cleaned_data:
                    review_topic = review_topic_form.instance
                    review_topic.review = review
                    review_topic.slug = update_slug(
                        ReviewTopic.objects.get(slug=review_topic.slug),
                        review_topic)
                    review_topic.save()

            return redirect(self.success_url)
        else:
            return self.form_invalid(form)


class ReviewDeleteView(
        PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Review
    template_name = 'review/review_delete.html'
    permission_required = ('review.delete_review',)
    login_url = reverse_lazy('users:login')
    success_url = reverse_lazy('review:all_reviews')

# ReviewTopic CRUD views


class ReviewTopicCreateView(
        PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = ReviewTopic
    form_class = AddReviewTopicForm
    template_name = 'review/review_topic_create.html'
    permission_required = ('add_reviewtopic',)

    def form_valid(self, form):
        """Save the form data and redirect to the success_url.
        The saved object is stored in `self.object` before redirecting.
        Return an HttpResponseRedirect to `success_url` if the form is valid.
        """
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """
        This method constructs the URL for the detail view of the review
        associated with the newly created review topic using the review's slug.

        Returns:
            str: The URL for the review detail page.
        """
        return reverse(
            'review:review', kwargs={'review_slug': self.object.review.slug})


class ReviewTopicUpdateView(
        PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = ReviewTopic
    form_class = EditReviewTopicForm
    template_name = 'review/review_topic_update.html'
    permission_required = ('change_reviewtopic',)

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        """
        Retrieves the ReviewTopic object based on the provided queryset
        and topic slug.

        Args:
            queryset: A QuerySet of objects or None.

        Returns:
            Model: The ReviewTopic object retrieved based on the topic slug.
        """
        return get_object_or_404(
            ReviewTopic.objects.select_related('review'),
            slug=self.kwargs['topic_slug'])

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'review:review', kwargs={'review_slug': self.object.review.slug})


class ReviewTopicDeleteView(
        PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = ReviewTopic
    template_name = 'review/review_topic_delete.html'
    permission_required = ('delete_reviewtopic',)
    success_url = reverse_lazy('review:all_reviews')

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return get_object_or_404(
            ReviewTopic, slug=self.kwargs['topic_slug'])


class CategoryListView(DataMixin, ListView):
    model = Category
    page_title = 'Categories'
    info_heading = 'Categories'
    context_object_name = 'categories'
    template_name = 'review/category_list.html'
    paginate_by = 10

    def get_queryset(self):
        """
        Retrieves all published categories from the cache or database.

        If the categories are not in the cache, it retrieves all published
        categories from the database and caches them.

        The categories are filtered using the CategoryFilter class, which
        filters the categories based on the GET parameters passed in the
        request.

        Returns:
            QuerySet: A queryset of all published categories filtered by the
            GET parameters.
        """
        category_list = cache.get('categories')
        if category_list is None:
            category_list = Category.objects.prefetch_related('reviews').all()
            cache.set('categories', category_list, timeout=60)
        self.filterset = CategoryFilter(
            self.request.GET, queryset=category_list)

        return self.filterset.qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        filter_data = self.request.GET.dict()
        context['filter_data'] = filter_data

        page = filter_data.get('page')
        name = filter_data.get('name', '')
        if page:
            self.info_heading = 'Categories'
        if name:
            self.info_heading = 'Searched for ' + filter_data['name'] \
                if filter_data else self.info_heading
        context['info_heading'] = self.info_heading

        return context


class CategoryDetailView(DataMixin, DetailView):
    model = Category
    template_name = 'review/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'category_slug'

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        """
        Retrieves the Category object based on the provided queryset
        and category slug.

        Args:
            queryset: A QuerySet of objects or None.

        Returns:
            Model: The Category object retrieved based on the category slug.
        """
        return get_object_or_404(
            Category.objects.prefetch_related('reviews'),
            slug=self.kwargs[self.slug_url_kwarg]
            )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(
            context, page_title="NewTekReviews - " + context['category'].name)


class CategoryCreateView(
        PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Category
    form_class = AddCategoryForm
    template_name = 'review/category_create.html'
    permission_required = ('add_category',)

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'review:category', kwargs={'category_slug': self.object.slug})


class CategoryUpdateView(
        PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Category
    form_class = AddCategoryForm
    template_name = 'review/category_update.html'
    permission_required = ('change_category',)

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return get_object_or_404(
            Category, slug=self.kwargs['category_slug'])

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'review:category', kwargs={'category_slug': self.object.slug})


class CategoryDeleteView(
        PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'review/category_delete.html'
    permission_required = ('delete_category',)
    success_url = reverse_lazy('review:categories')

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return get_object_or_404(
            Category, slug=self.kwargs['category_slug'])


class ContactFormView(LoginRequiredMixin, FormView):
    form_class = ContactForm
    template_name = 'review/contact.html'
    success_url = reverse_lazy('review:all_reviews')

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)
