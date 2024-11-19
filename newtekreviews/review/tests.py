from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils.text import slugify
from mixer.backend.django import mixer

from .models import Review, ReviewTopic, Category
from .forms import AddReviewForm, UpdateReviewTopicFormSet

# Tests for the Review CRUD


class GetAllReviewsTestCase(TestCase):
    def setUp(self):
        self.reviews = mixer.cycle(5).blend(Review, is_published=True)

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
        self.assertQuerySetEqual(
            list(response.context_data['reviews']), review_list)
        self.assertEqual(len(response.context_data['reviews']), 5)

    def tearDown(self) -> None:
        pass


class GetReviewTestCase(TestCase):
    def setUp(self):
        self.review = mixer.blend(
            Review, slug=slugify('Test Review'), is_published=True)

    def test_get_review(self):
        path = reverse(
            'review:review', kwargs={'review_slug': self.review.slug})
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'review/review_detail.html')

    def tearDown(self) -> None:
        pass


class CreateReviewTestCase(TestCase):
    def setUp(self):
        self.user = mixer.blend(get_user_model(), is_superuser=True)
        self.category = mixer.blend(Category)
        self.client.force_login(self.user)
        self.data = {
            'title': 'Test Review',
            'description': 'Test content',
            'main_image': '',
            'is_published': True,
            'category': self.category.pk,
        }
        self.data.update({
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
        })

    def test_create_review(self):
        """
        Test that the 'review:review_create' URL returns a 302 HTTP status
        response and creates a new Review that is published and redirects to
        the 'review:all_reviews' URL.
        """

        path = reverse('review:review_create')
        response = self.client.post(path, data=self.data)
        print(response.content)
        if response.status_code != HTTPStatus.FOUND:
            print("Form errors:", response.context_data['form'].errors)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            Review.objects.filter(title=self.data['title']).exists())
        self.assertRedirects(response, reverse('review:all_reviews'))

    def tearDown(self) -> None:
        self.client.logout()
        self.category.delete()
        self.user.delete()


class ReviewCreateViewTestCase(TestCase):
    def setUp(self):
        # Set up user with required permissions
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@localhost',
            password='testpass'
        )
        self.user.user_permissions.add(
            Permission.objects.get(codename='add_review'))
        self.user.user_permissions.add(
            Permission.objects.get(codename='add_reviewtopic'))

        self.client.login(username='testuser', password='testpass')

        # Create category for testing
        self.category = Category.objects.create(name='Test Category')

        self.url = reverse('review:review_create')

    def tearDown(self) -> None:
        self.client.logout()
        self.user.delete()
        self.category.delete()

    def test_login_required(self):
        """
        Tests that the view requires the user to be logged in.

        The test logs out the client, then attempts to access the view.
        The response should redirect to the login page with the next
        parameter set to the original URL.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/auth/login/?next={self.url}')

    def test_permission_required(self):
        """
        Tests that the view requires the user to have the 'add_review' permission.

        The test first removes the 'add_review' permission from the user, then
        attempts to access the view. The response should have a status code of
        403.
        """

        self.user.user_permissions.remove(
            Permission.objects.get(codename='add_review'))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_form_and_formset_display(self):
        """
        Tests that the form and formset are correctly displayed in the response.

        This test makes a GET request to the 'review:review_create' URL and verifies:
        - The response status code is 200 (OK).
        - The 'review/review_create.html' template is used.
        - The context includes 'review_topic_formset'.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review/review_create.html')
        self.assertIn('review_topic_formset', response.context)


class ReviewUpdateViewTestCase(TestCase):
    def setUp(self):
        # Set up user with required permissions
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@localhost',
            password='testpass'
        )
        self.user.user_permissions.add(
            Permission.objects.get(codename='change_review'))
        self.user.user_permissions.add(
            Permission.objects.get(codename='add_reviewtopic'))
        self.user.user_permissions.add(
            Permission.objects.get(codename='change_reviewtopic'))

        self.client.login(username='testuser', password='testpass')

        # Create category, review, and review topic for testing
        self.category = Category.objects.create(name='Test Category')
        self.review = Review.objects.create(
            title='Test Review', slug='test-review',
            description='Initial content', main_image='',
            is_published=True, author=self.user, category=self.category
        )
        self.review_topic = ReviewTopic.objects.create(
            review=self.review,
            review_topic_title='Test Topic',
            text_content='Initial text content'
        )
        self.url = reverse(
            'review:review_update', kwargs={'slug': self.review.slug})

    def tearDown(self) -> None:
        self.client.logout()
        self.user.delete()
        self.category.delete()
        self.review.delete()
        self.review_topic.delete()

    def test_login_required(self):
        """
        Tests that the view requires the user to be logged in.

        The test first logs the client out, then attempts to access the view.
        The response should redirect to the login view with the current URL as
        the 'next' parameter.
        """

        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/auth/login/?next={self.url}')

    def test_permission_required(self):
        """
        Tests that the view requires the user to have the 'change_review'
        permission.

        The test first removes the 'change_review' permission from the user,
        then attempts to access the view. The response should have a status
        code of 403.
        """

        self.user.user_permissions.remove(
            Permission.objects.get(codename='change_review'))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_form_and_formset_display(self):
        """
        Tests that the form and formset are correctly displayed in the response.

        This test makes a GET request to the 'review:review_update' URL and verifies:
        - The response status code is 200 (OK).
        - The 'review/review_update.html' template is used.
        - The context includes 'review_topic_formset'.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review/review_update.html')
        self.assertIn('review_topic_formset', response.context)

    def test_valid_form_and_formset_submission(self):
        """
        Tests that submitting a valid form and formset updates the related
        `Review` and `ReviewTopic` instances and redirects to the success URL.

        The test creates a valid form and formset, posts the data to the view,
        verifies that the form and formset are valid, checks that the response
        is a redirect to the success URL, and verifies that the related
        `Review` and `ReviewTopic` instances are updated in the database.
        """

        form_data = {
            'title': 'Updated Review',
            'description': 'Updated description',
            'main_image': '',
            'is_published': True,
            'category': self.category.id,
        }
        formset_data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-id': self.review_topic.pk,
            'form-0-review_topic_title': 'Updated Topic',
            'form-0-text_content': 'Updated text content',
            'form-0-DELETE': '',
        }

        form = AddReviewForm(data=form_data)
        formset = UpdateReviewTopicFormSet(data=formset_data)

        post_data = {**form_data, **formset_data}

        response = self.client.post(self.url, post_data)

        self.assertTrue(form.is_valid())
        self.assertTrue(formset.is_valid())

        self.assertEqual(response.status_code, 302)

        # Check redirection to success URL
        self.assertRedirects(response, reverse('review:all_reviews'))

        # Verify updates in the database
        updated_review = Review.objects.get(pk=self.review.pk)
        self.assertEqual(updated_review.title, 'Updated Review')
        self.assertEqual(updated_review.description, 'Updated description')

        updated_review_topic = ReviewTopic.objects.get(pk=self.review_topic.pk)
        self.assertEqual(
            updated_review_topic.review_topic_title, 'Updated Topic')
        self.assertEqual(
            updated_review_topic.text_content, 'Updated text content')

    def test_deletion_of_review_topic_in_formset(self):
        """
        Test that a ReviewTopic instance is deleted when marked for deletion
        in the UpdateReviewTopicFormSet on the ReviewUpdateView.

        This test creates a ReviewTopicFormSet with one form, marks the
        form for deletion, and posts the form data to the ReviewUpdateView.
        It asserts that the ReviewTopic instance is deleted and that the
        view redirects to the all_reviews URL.
        """

        form_data = {
            'title': 'Updated Review',
            'description': 'Updated description',
            'main_image': '',
            'is_published': True,
            'category': self.category.id,
        }
        formset_data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-id': self.review_topic.id,
            'form-0-review_topic_title': 'Updated Topic',
            'form-0-text_content': 'Updated text content',
            'form-0-DELETE': 'on',  # Mark for deletion
        }
        post_data = {**form_data, **formset_data}

        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, reverse('review:all_reviews'))

        # Verify the ReviewTopic has been deleted
        with self.assertRaises(ReviewTopic.DoesNotExist):
            ReviewTopic.objects.get(pk=self.review_topic.pk)

        self.assertFalse(
            ReviewTopic.objects.filter(review_topic_title='Updated Topic')
            .exists())


class ReviewDeleteViewTestCase(TestCase):
    def setUp(self):
        self.user = mixer.blend(get_user_model())
        self.user.user_permissions.add(
            Permission.objects.get(codename='delete_review'))
        self.review = mixer.blend(Review)
        self.review_topic = mixer.blend(ReviewTopic, review=self.review)
        self.client.force_login(self.user)
        self.url = reverse('review:review_delete', args=[self.review.slug])

    def test_delete_review(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('review:all_reviews'))
        self.assertFalse(Review.objects.filter(slug=self.review.slug).exists())
        self.assertFalse(
            ReviewTopic.objects.filter(review=self.review).exists())

    def tearDown(self) -> None:
        self.client.logout()
        self.user.delete()
        self.review.delete()
        self.review_topic.delete()


#  Tests for the Category CRUD


class GetAllCategoriesTestCase(TestCase):
    def setUp(self):
        self.categories = mixer.cycle(5).blend(
            Category, category_background='background.png')

    def test_get_all_categories(self):
        """
        Test that the 'review:categories' URL returns a 200 HTTP status response
        and renders the 'review/category_list.html' template with the correct
        page title.
        """

        path = reverse('review:categories')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('review/category_list.html', response.template_name)
        self.assertTemplateUsed(response, 'review/category_list.html')
        self.assertEqual(response.context_data['page_title'], 'Categories')

    def test_data_all_categories(self):
        """
        Test that the 'review:categories' URL returns a QuerySet of all
        Categories ordered by 'name' in ascending order.
        """

        category_list = Category.objects.prefetch_related('reviews').all()
        path = reverse('review:categories')
        response = self.client.get(path)
        self.assertQuerySetEqual(
            list(response.context_data['categories']), category_list)

    def tearDown(self) -> None:
        pass


class GetCategoryTestCase(TestCase):
    def setUp(self):
        self.category = mixer.blend(
            Category, category_background='background.png')

    def test_get_category(self):
        """
        Test that the 'review:category' URL returns a 200 HTTP status response
        and renders the 'review/category_detail.html' template for the given
        category slug.
        """
        path = reverse(
            'review:category', kwargs={'category_slug': self.category.slug})
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'review/category_detail.html')

    def tearDown(self) -> None:
        pass


class CategoryCreateViewTestCase(TestCase):
    def setUp(self):
        self.user = mixer.blend(get_user_model(), is_superuser=True)
        self.client.force_login(self.user)
        self.url = reverse('review:category_create')

    def test_create_category(self):
        data = {
            'name': 'Test Category',
            'category_background': 'background.png'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, reverse(
                'review:category', kwargs={'category_slug': 'test-category'}))
        self.assertTrue(
            Category.objects.filter(name=data['name']).exists())

    def tearDown(self) -> None:
        self.client.logout()
        self.user.delete()


class CategoryUpdateViewTestCase(TestCase):
    def setUp(self):
        self.category = mixer.blend(
            Category, category_background='background.png')
        self.user = mixer.blend(get_user_model(), is_superuser=True)
        self.client.force_login(self.user)
        self.url = reverse(
            'review:category_update',
            kwargs={'category_slug': self.category.slug})

        self.data = {
            'name': 'Updated Category',
            'category_background': 'background.png'
        }

    def test_update_category(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, reverse(
                'review:category',
                kwargs={'category_slug': self.category.slug}))
        self.assertTrue(
            Category.objects.filter(name=self.data['name']).exists())

    def tearDown(self) -> None:
        self.client.logout()
        self.user.delete()
        self.category.delete()


class CategoryDeleteViewTestCase(TestCase):
    def setUp(self):
        self.category = mixer.blend(
            Category, category_background='background.png')
        self.user = mixer.blend(get_user_model(), is_superuser=True)
        self.client.force_login(self.user)
        self.url = reverse(
            'review:category_delete',
            kwargs={'category_slug': self.category.slug})

    def test_delete_category(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, reverse('review:categories'))
        self.assertFalse(
            Category.objects.filter(slug=self.category.slug).exists())

    def tearDown(self) -> None:
        self.client.logout()
        self.user.delete()
        self.category.delete()
