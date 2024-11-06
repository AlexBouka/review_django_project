from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from django.contrib.auth import get_user_model


class UserRegisterTestCase(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.data = {
            'username': 'user_11',
            'email': 'testuser@example.com',
            'first_name': 'John',
            'last_name': 'Tester',
            'password1': '!b87654321',
            'password2': '!b87654321',
        }

    def test_form_registration_get(self):
        path = reverse('users:register')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/user_registration.html')

    def test_user_registration_success(self):
        path = reverse('users:register')
        response = self.client.post(path, data=self.data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(
            self.user_model.objects.filter(
                username=self.data['username']).exists()
                )

    def test_user_registration_password_error(self):
        self.data['password2'] = '!b12345678'
        path = reverse('users:register')
        response = self.client.post(path, data=self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, 'The two password fields didn’t match.', html=False)

    def test_same_username_registration_error(self):
        self.user_model.objects.create_user(username=self.data['username'])
        path = reverse('users:register')
        response = self.client.post(path, data=self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, 'A user with that username already exists.', html=False)
