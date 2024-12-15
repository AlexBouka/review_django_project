from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse

from .serializers import UserSerializer

User = get_user_model()


class CustomAuthTokenViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('newtek_api:custom_token_auth')
        self.user = User.objects.create_user(
            username='testuser', password='testpass123')

    def test_valid_credentials(self):
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(Token.objects.count(), 1)
        self.assertEqual(Token.objects.first().user, self.user)

    def test_invalid_credentials(self):
        data = {'username': 'wronguser', 'password': 'wrongpass'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'error': 'Invalid credentials'})
        self.assertEqual(Token.objects.count(), 0)

    def test_empty_credentials(self):
        data = {'username': '', 'password': ''}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'error': 'Invalid credentials'})
        self.assertEqual(Token.objects.count(), 0)

    def test_non_existent_username(self):
        data = {'username': 'nonexistentuser', 'password': 'somepassword'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'error': 'Invalid credentials'})
        self.assertEqual(Token.objects.count(), 0)

    def test_correct_username_incorrect_password(self):
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'error': 'Invalid credentials'})
        self.assertEqual(Token.objects.count(), 0)

    def test_create_new_token(self):
        # Delete any existing tokens for the user
        Token.objects.filter(user=self.user).delete()

        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(Token.objects.count(), 1)
        self.assertEqual(Token.objects.first().user, self.user)

        # Verify that the token in the response matches the newly created token
        new_token = Token.objects.get(user=self.user)
        self.assertEqual(response.data['token'], new_token.key)

    def test_existing_token(self):
        # Create a token for the user
        existing_token = Token.objects.create(user=self.user)

        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['token'], existing_token.key)
        self.assertEqual(Token.objects.count(), 1)
        self.assertEqual(Token.objects.first(), existing_token)

    def test_special_characters_in_credentials(self):
        special_user = User.objects.create_user(
            username='test@user!', password='p@ssw0rd!')
        data = {'username': 'test@user!', 'password': 'p@ssw0rd!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'test@user!')
        self.assertEqual(Token.objects.count(), 1)
        self.assertEqual(Token.objects.first().user, special_user)

    def test_serialized_user_data_in_response(self):
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        user_serializer = UserSerializer(self.user)
        self.assertEqual(response.data['user'], user_serializer.data)
