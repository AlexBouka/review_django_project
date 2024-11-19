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
        """
        Tests the GET request to the user registration page.

        This test verifies that the registration page is accessible and uses
        the correct template. It makes a GET request to the registration URL
        and checks that the response status code is 200 (OK) and that the
        'users/user_registration.html' template is used in the response.
        """

        path = reverse('users:register')
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/user_registration.html')

    def test_user_registration_success(self):
        """
        Tests the successful registration of a new user.

        This test makes a POST request to the user registration URL with valid
        user data. It verifies that the response status code is 302 (FOUND),
        indicating a redirect, and that the user is redirected to the login page.
        It also checks that a new user with the given username exists in the
        database.
        """

        path = reverse('users:register')
        response = self.client.post(path, data=self.data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(
            self.user_model.objects.filter(
                username=self.data['username']).exists()
                )

    def test_user_registration_password_error(self):
        """
        Tests the user registration with an invalid password.

        This test makes a POST request to the user registration URL with a
        valid username, email, and first and last name, but with different
        passwords in the two password fields. It verifies that the response
        status code is 200 (OK) and that the response contains an error
        message indicating that the two password fields didn't match.
        """

        self.data['password2'] = '!b12345678'
        path = reverse('users:register')
        response = self.client.post(path, data=self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, 'The two password fields didn’t match.', html=False)

    def test_same_username_registration_error(self):
        """
        Tests the registration process with an already existing username.

        This test creates a user with an existing username and then attempts to
        register a new user with the same username. It verifies that the response
        status code is 200 (OK) and that the response contains an error message
        indicating that a user with that username already exists.
        """

        self.user_model.objects.create_user(username=self.data['username'])
        path = reverse('users:register')
        response = self.client.post(path, data=self.data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, 'A user with that username already exists.', html=False)

    def tearDown(self):
        pass
