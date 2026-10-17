"""
Automated tests for Patient-Doctor Mapping APIs, duplicate protection, and ownership rules.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping

class MappingTests(APITestCase):
    def setUp(self):
        self.list_create_url = reverse('mapping-list-create')

        # Users
        self.user_a = User.objects.create_user(
            username='coordinator_a@careos.health',
            email='coordinator_a@careos.health',
            first_name='Coordinator A',
            password='Password123!'
        )
        self.user_b = User.objects.create_user(
            username='coordinator_b@careos.health',
            email='coordinator_b@careos.health',
            first_name='Coordinator B',
            password='Password123!'
        )

        # Patients
        self.patient_a = Patient.objects.create(
            created_by=self.user_a,
            name='Robert Chase',
            age=32,
            gender='Male',
            phone='+1-555-1111',
            address='100 Hospital Way'
        )
        self.patient_b = Patient.objects.create(
            created_by=self.user_b,
            name='Allison Cameron',
            age=30,
            gender='Female',
            phone='+1-555-2222',
            address='200 Clinic Rd'
        )

        # Doctors
        self.doctor_1 = Doctor.objects.create(
            created_by=self.user_a,
            name='Dr. Lisa Cuddy',
            specialization='Endocrinology',
            email='cuddy@careos.health',
            phone='+1-555-3333',
            experience_years=15
        )
        self.doctor_2 = Doctor.objects.create(
            created_by=self.user_a,
            name='Dr. Eric Foreman',
            specialization='Neurology',
            email='foreman@careos.health',
            phone='+1-555-4444',
            experience_years=12
        )

    def test_unauthenticated_request_fails(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_assign_doctor_to_owned_patient_success(self):
        self.client.force_authenticate(user=self.user_a)
        payload = {
            'patient': self.patient_a.id,
            'doctor': self.doctor_1.id
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['patient'], self.patient_a.id)
        self.assertEqual(response.data['data']['doctor'], self.doctor_1.id)

    def test_assign_doctor_to_other_user_patient_fails(self):
        # User A tries to assign doctor to Patient B (owned by User B)
        self.client.force_authenticate(user=self.user_a)
        payload = {
            'patient': self.patient_b.id,
            'doctor': self.doctor_1.id
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_duplicate_mapping_rejected(self):
        self.client.force_authenticate(user=self.user_a)
        payload = {
            'patient': self.patient_a.id,
            'doctor': self.doctor_1.id
        }
        # First assignment succeeds
        res1 = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        # Duplicate assignment must fail
        res2 = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(res2.data['success'])

    def test_get_mappings_for_patient(self):
        # Assign 2 doctors to patient_a
        PatientDoctorMapping.objects.create(patient=self.patient_a, doctor=self.doctor_1, assigned_by=self.user_a)
        PatientDoctorMapping.objects.create(patient=self.patient_a, doctor=self.doctor_2, assigned_by=self.user_a)

        self.client.force_authenticate(user=self.user_a)
        url = reverse('mapping-detail', kwargs={'pk': self.patient_a.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['doctors']), 2)

    def test_delete_mapping_success(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_1,
            assigned_by=self.user_a
        )
        self.client.force_authenticate(user=self.user_a)
        url = reverse('mapping-detail', kwargs={'pk': mapping.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping.id).exists())

    def test_delete_mapping_by_unauthorized_user_fails(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient_a,
            doctor=self.doctor_1,
            assigned_by=self.user_a
        )
        # User B attempts to delete User A's mapping
        self.client.force_authenticate(user=self.user_b)
        url = reverse('mapping-detail', kwargs={'pk': mapping.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(PatientDoctorMapping.objects.filter(id=mapping.id).exists())
