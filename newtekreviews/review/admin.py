from io import TextIOWrapper
import csv

from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect
from django.urls import path

from .models import Review, Category, ReviewTopic
from .forms import CSVForm


class ReviewCategoryFilter(admin.SimpleListFilter):
    title = "category"
    parameter_name = "category"

    def lookups(self, request, model_admin):
        return [
            Category.objects.values_list('name', flat=True)
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category__name=self.value())
        return queryset


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    change_list_template = 'admin/reviews_changelist.html'
    list_display = (
        "id", "title", "description",
        "review_main_image", "author", "time_created",
        "time_updated", "is_published", "category",
        )
    list_display_links = ("title",)
    list_editable = ("is_published",)
    list_filter = (ReviewCategoryFilter, "is_published", "category",)
    search_fields = ("title__startswith", "description",)
    prepopulated_fields = {"slug": ("title",)}

    @admin.display(description="Main Image")
    def review_main_image(self, review: Review):
        if review.main_image:
            return mark_safe(f"<img src='{review.main_image.url}' width=100")
        return "No Image"

    @admin.action(description="Make selected reviews published")
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Review.Status.PUBLISHED)
        self.message_user(
            request, f"{count} reviews were successfully published",
            messages.SUCCESS
            )

    @admin.action(description="Make selected reviews unpublished")
    def set_unpublished(self, request, queryset):
        count = queryset.update(is_published=Review.Status.DRAFT)
        self.message_user(
            request, f"{count} reviews were successfully unpublished",
            messages.WARNING
            )

    actions = ("set_published", "set_unpublished", )

    def import_csv(self, request):
        if request.method == "GET":
            form = CSVForm()
            context = {
                "form": form
            }
            return render(request, "admin/csv_form.html", context)

        form = CSVForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form
            }
            return render(request, "admin/csv_form.html", context, status=400)

        csv_file = TextIOWrapper(
            form.files['csv_file'].file, encoding=request.encoding)
        reader = csv.DictReader(csv_file)

        reviews = [
            Review(**row) for row in reader
        ]
        Review.objects.bulk_create(reviews)
        self.message_user(
            request, "Reviews successfully imported", messages.SUCCESS
        )

        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import_review_csv/", self.import_csv,
                name="import_review_csv"),
        ]

        return new_urls + urls


@admin.register(ReviewTopic)
class ReviewTopicAdmin(admin.ModelAdmin):
    list_display = ("review_topic_title", "review", "text_content", "slug")
    list_display_links = ("review_topic_title",)
    search_fields = ("review_topic_title__startswith", "text_content")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    list_display_links = ("name",)
    list_filter = ("name",)
    search_fields = ("name__startswith",)
    prepopulated_fields = {"slug": ("name",)}
