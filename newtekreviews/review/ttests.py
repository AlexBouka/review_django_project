from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission
from review.models import Review, ReviewTopic, Category
from review.forms import AddReviewForm, UpdateReviewTopicFormSet


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

    def tearDown(self):
        self.client.logout()
        self.user.delete()
        self.category.delete()

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/auth/login/?next={self.url}')

    def test_permission_required(self):
        self.user.user_permissions.remove(
            Permission.objects.get(codename='add_review'))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_form_and_formset_display(self):
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

    def tearDown(self):
        self.client.logout()
        self.user.delete()
        self.category.delete()
        self.review.delete()
        self.review_topic.delete()

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/auth/login/?next={self.url}')

    def test_permission_required(self):
        self.user.user_permissions.remove(
            Permission.objects.get(codename='change_review'))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_form_and_formset_display(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review/review_update.html')
        self.assertIn('review_topic_formset', response.context)

    def test_valid_form_and_formset_submission(self):
        # Data for updating the Review and ReviewTopic instances
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
