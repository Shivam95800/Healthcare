"""
Automated tests for Doctor CRUD APIs and creator authorization.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from doctors.models import Doctor

class DoctorTests(APITestCase):
    def setUp(self):
        self.list_create_url = reverse('doctor-list-create')

        self.user_a = User.objects.create_user(
            username='dr_creator@careos.health',
            email='dr_creator@careos.health',
            first_name='Dr. Creator',
            password='Password123!'
        )

        self.user_b = User.objects.create_user(
            username='viewer@careos.health',
            email='viewer@careos.health',
            first_name='Viewer User',
            password='Password123!'
        )

        self.doctor = Doctor.objects.create(
            created_by=self.user_a,
            name='Gregory House',
            specialization='Diagnostic Medicine',
            email='house@princetonplainsboro.org',
            phone='+1-555-0800',
            experience_years=20
        )

    def test_unauthenticated_request_fails(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_doctor_success(self):
        self.client.force_authenticate(user=self.user_a)
        payload = {
            'name': 'James Wilson',
            'specialization': 'Oncology',
            'email': 'wilson@princetonplainsboro.org',
            'phone': '+1-555-0801',
            'experience_years': 18
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], 'James Wilson')

    def test_list_doctors_returns_all_doctors(self):
        self.client.force_authenticate(user=self.user_b)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Even though user_b didn't create doctor, user_b can see all doctors
        results = response.data['results']
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]['email'], 'house@princetonplainsboro.org')

    def test_view_doctor_details_any_authenticated_user(self):
        self.client.force_authenticate(user=self.user_b)
        url = reverse('doctor-detail', kwargs={'pk': self.doctor.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Gregory House')

    def test_update_doctor_by_non_creator_fails(self):
        self.client.force_authenticate(user=self.user_b)
        url = reverse('doctor-detail', kwargs={'pk': self.doctor.id})
        payload = {
            'name': 'Modified House',
            'specialization': 'Neurology',
            'email': 'house@princetonplainsboro.org',
            'phone': '+1-555-0800',
            'experience_years': 25
        }
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_doctor_by_non_creator_fails(self):
        self.client.force_authenticate(user=self.user_b)
        url = reverse('doctor-detail', kwargs={'pk': self.doctor.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Doctor.objects.filter(id=self.doctor.id).exists())

    def test_update_doctor_by_creator_success(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse('doctor-detail', kwargs={'pk': self.doctor.id})
        payload = {
            'name': 'Gregory House MD',
            'specialization': 'Diagnostic Medicine & Nephrology',
            'email': 'house@princetonplainsboro.org',
            'phone': '+1-555-0800',
            'experience_years': 21
        }
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'Gregory House MD')

    def test_delete_doctor_by_creator_success(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse('doctor-detail', kwargs={'pk': self.doctor.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Doctor.objects.filter(id=self.doctor.id).exists())
