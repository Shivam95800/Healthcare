"""
Automated tests for Patient CRUD and Ownership Isolation.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from patients.models import Patient

class PatientTests(APITestCase):
    def setUp(self):
        self.list_create_url = reverse('patient-list-create')

        # User A
        self.user_a = User.objects.create_user(
            username='user_a@careos.health',
            email='user_a@careos.health',
            first_name='User A',
            password='Password123!'
        )

        # User B
        self.user_b = User.objects.create_user(
            username='user_b@careos.health',
            email='user_b@careos.health',
            first_name='User B',
            password='Password123!'
        )

        # Patient created by User A
        self.patient_a = Patient.objects.create(
            created_by=self.user_a,
            name='John Doe',
            age=34,
            gender='Male',
            phone='+1-555-0100',
            address='123 Main St, Springfield',
            medical_history='Mild hypertension'
        )

        # Patient created by User B
        self.patient_b = Patient.objects.create(
            created_by=self.user_b,
            name='Jane Smith',
            age=29,
            gender='Female',
            phone='+1-555-0200',
            address='456 Elm St, Metropolis',
            medical_history='Asthma'
        )

    def test_unauthenticated_request_fails(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_auto_sets_created_by(self):
        self.client.force_authenticate(user=self.user_a)
        payload = {
            'name': 'Sam Wilson',
            'age': 45,
            'gender': 'Male',
            'phone': '+1-555-0300',
            'address': '789 Oak Ave, Star City',
            'medical_history': 'No prior conditions'
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], 'Sam Wilson')
        self.assertEqual(response.data['data']['created_by'], self.user_a.id)

    def test_list_patients_only_returns_owned_records(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results should be paginated
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.patient_a.id)

    def test_retrieve_patient_detail_owner_success(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse('patient-detail', kwargs={'pk': self.patient_a.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Doe')

    def test_retrieve_other_user_patient_forbidden(self):
        self.client.force_authenticate(user=self.user_a)
        # Attempt to access User B's patient
        url = reverse('patient-detail', kwargs={'pk': self.patient_b.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_other_user_patient_forbidden(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse('patient-detail', kwargs={'pk': self.patient_b.id})
        payload = {'name': 'Hacked Name', 'age': 50, 'gender': 'Male', 'phone': '000', 'address': 'Nowhere'}
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_other_user_patient_forbidden(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse('patient-detail', kwargs={'pk': self.patient_b.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Ensure still exists in DB
        self.assertTrue(Patient.objects.filter(id=self.patient_b.id).exists())

    def test_update_own_patient_success(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse('patient-detail', kwargs={'pk': self.patient_a.id})
        payload = {
            'name': 'John Doe Updated',
            'age': 35,
            'gender': 'Male',
            'phone': '+1-555-9999',
            'address': '123 Main St, Springfield Updated',
            'medical_history': 'Resolved hypertension'
        }
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'John Doe Updated')

    def test_delete_own_patient_success(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse('patient-detail', kwargs={'pk': self.patient_a.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Patient.objects.filter(id=self.patient_a.id).exists())
