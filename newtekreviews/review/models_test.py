from django.test import TestCase
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from review.models import Review, ReviewTopic, Category


class ReviewModelTest(TestCase):
    def setUp(self):
        self.review = Review.objects.create(title="Test Review")

    def tearDown(self):
        self.review.delete()

    def test_save_method_handles_special_characters(self):
        review = Review(title="Test Review: Special Characters !@#$%^&*()")
        review.save()
        self.assertEqual(review.slug, "test-review-special-characters")
        self.assertTrue(Review.objects.filter(slug=review.slug).exists())

    def test_save_method_creates_unique_slug(self):
        review1 = Review(title="Test Review")
        review1.save()
        review2 = Review(title="Test Review")
        review2.save()
        self.assertNotEqual(review1.slug, review2.slug)
        self.assertTrue(Review.objects.filter(slug=review1.slug).exists())
        self.assertTrue(Review.objects.filter(slug=review2.slug).exists())

    def test_save_method_handles_non_ascii_characters(self):
        review = Review(title="Test Review with non-ASCII charactersに日本語")
        review.save()
        self.assertEqual(review.slug, "test-review-with-non-ascii-characters")
        self.assertTrue(Review.objects.filter(slug=review.slug).exists())

    def test_str_method(self):
        review = Review(title="Test Review")
        self.assertEqual(str(review), "Test Review")


class ReviewTopicModelTest(TestCase):
    def setUp(self):
        self.review = Review.objects.create(title="Test Review")
        self.review.save()
        self.review_topic = ReviewTopic.objects.create(
            review=self.review, review_topic_title="Test Topic")

    def tearDown(self):
        self.review_topic.delete()

    def test_review_topic_creation(self):
        self.review_topic.save()
        self.assertTrue(
            ReviewTopic.objects.filter(review_topic_title="Test Topic")
            .exists())

    def test_review_topic_relationship(self):
        self.review_topic.save()
        self.assertEqual(self.review_topic.review, self.review)

    def test_review_topic_cascade_delete(self):
        self.review_topic.save()
        review_id = self.review.id
        self.review.delete()
        self.assertFalse(
            ReviewTopic.objects.filter(review=review_id).exists())

    def test_review_topic_str_method(self):
        self.assertEqual(str(self.review_topic), "Test Topic")


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def tearDown(self):
        self.category.delete()

    def test_category_creation(self):
        self.category.save()
        self.assertTrue(Category.objects.filter(name="Test Category").exists())

    def test_category_slug_generation(self):
        self.category.save()
        self.assertEqual(self.category.slug, slugify("Test Category"))

    def test_category_str_method(self):
        self.assertEqual(str(self.category), "Test Category")
