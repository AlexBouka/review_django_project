from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils.text import slugify

from .models import Review, Category
from .forms import AddReviewForm


class GetAllReviewsTestCase(TestCase):
    fixtures = [
        "fixtures/db.json"
    ]

    def setUp(self):
        pass

    def test_get_all_reviews(self):
        """
        Test that the 'review:all_reviews' URL returns a 200 HTTP status response
        and renders the 'review/review_list.html' template with the correct
        page title.
        """
        path = reverse('review:all_reviews')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('review/review_list.html', response.template_name)
        self.assertTemplateUsed(response, 'review/review_list.html')
        self.assertEqual(response.context_data['page_title'], 'All Reviews')

    def test_data_all_reviews(self):
        """
        Test that the 'review:all_reviews' URL returns a QuerySet of Reviews that
        are published and are paginated to 5 items per page. The first page
        should contain the first 2 items of the QuerySet sorted by
        'time_created' in descending order.
        """

        review_list = Review.published.all().select_related('category')
        path = reverse('review:all_reviews')
        response = self.client.get(path)
        self.assertQuerysetEqual(
            list(response.context_data['reviews']), review_list[:2])

    def test_get_all_reviews_pagination(self):
        """
        Test that the 'review:all_reviews' URL returns a QuerySet of Reviews that
        are paginated to 5 items per page. The first page should contain the first
        5 items of the QuerySet sorted by 'time_created' in descending order and
        the second page should contain the next 5 items of the QuerySet and so
        on.
        """

        path = reverse('review:all_reviews')
        page = 1
        paginate_by = 5
        response = self.client.get(path + f'?page={page}')
        review_list = Review.published.all().select_related('category')
        self.assertQuerysetEqual(
            list(response.context_data['reviews']),
            list(review_list[paginate_by * (page - 1):paginate_by * page])
        )

    def tearDown(self):
        pass


class GetReviewTestCase(TestCase):
    fixtures = [
        "fixtures/db.json"
    ]

    def setUp(self):
        self.slug = Review.published.first().slug

    def test_get_review(self):
        path = reverse('review:review', args=[self.slug])
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'review/review_detail.html')

    def tearDown(self):
        pass


class CreateReviewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testuser', password='testpass1!')
        self.user.is_superuser = True
        self.user.save()
        self.category = Category.objects.create(
            name='Test Category',
            slug=slugify('test-category')
        )
        self.client.force_login(self.user)
        self.data = {
            AddReviewForm.Meta.fields[0]: 'Test Review',
            AddReviewForm.Meta.fields[1]: 'test-review',
            AddReviewForm.Meta.fields[2]: 'Test content',
            AddReviewForm.Meta.fields[3]: '',
            AddReviewForm.Meta.fields[4]: True,
            AddReviewForm.Meta.fields[5]: self.category.id,
        }

    def test_create_review(self):
        """
        Test that the 'review:review_create' URL returns a 302 HTTP status
        response and creates a new Review that is published and redirects to
        the 'review:all_reviews' URL.
        """
        path = reverse('review:review_create')
        response = self.client.post(path, data=self.data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            Review.published.filter(title=self.data['title']).exists())
        self.assertRedirects(response, reverse('review:all_reviews'))

    def tearDown(self):
        self.client.logout()
        self.category.delete()
        self.user.delete()
