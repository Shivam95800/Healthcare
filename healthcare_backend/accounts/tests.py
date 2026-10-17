"""
Automated tests for Authentication and User APIs.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.user_data = {
            'name': 'Dr. Alice Carter',
            'email': 'alice@careos.health',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertEqual(response.data['user']['email'], 'alice@careos.health')
        self.assertEqual(response.data['user']['name'], 'Dr. Alice Carter')

        # Check DB
        self.assertTrue(User.objects.filter(email='alice@careos.health').exists())

    def test_register_duplicate_email_fails(self):
        # Register once
        self.client.post(self.register_url, self.user_data, format='json')
        # Register second time
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_register_password_mismatch_fails(self):
        mismatch_data = self.user_data.copy()
        mismatch_data['confirm_password'] = 'DifferentPassword999!'
        response = self.client.post(self.register_url, mismatch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_login_user_success(self):
        # Register first
        self.client.post(self.register_url, self.user_data, format='json')

        # Login
        login_payload = {
            'email': 'alice@careos.health',
            'password': 'SecurePassword123!'
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_password_fails(self):
        self.client.post(self.register_url, self.user_data, format='json')

        login_payload = {
            'email': 'alice@careos.health',
            'password': 'WrongPassword123'
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
