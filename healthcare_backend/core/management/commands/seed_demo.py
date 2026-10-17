"""
Management command to seed demo data into CareOS.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping

class Command(BaseCommand):
    help = 'Seeds initial demonstration users, patients, doctors and mappings into PostgreSQL.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding CareOS demo data...")

        # 1. Demo User
        user, created = User.objects.get_or_create(
            username='doctor@careos.health',
            defaults={
                'email': 'doctor@careos.health',
                'first_name': 'Dr. Sarah Connor'
            }
        )
        if created:
            user.set_password('CareOS2026!')
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created demo user: {user.email} (Password: CareOS2026!)"))
        else:
            self.stdout.write(f"Demo user {user.email} already exists.")

        # 2. Doctors
        doctors_data = [
            {
                'name': 'Gregory House',
                'specialization': 'Diagnostic Medicine',
                'email': 'house@careos.health',
                'phone': '+1 (555) 018-4921',
                'experience_years': 20
            },
            {
                'name': 'James Wilson',
                'specialization': 'Oncology',
                'email': 'wilson@careos.health',
                'phone': '+1 (555) 018-8422',
                'experience_years': 18
            },
            {
                'name': 'Lisa Cuddy',
                'specialization': 'Endocrinology',
                'email': 'cuddy@careos.health',
                'phone': '+1 (555) 018-7733',
                'experience_years': 15
            }
        ]

        created_doctors = []
        for d in doctors_data:
            doc, _ = Doctor.objects.get_or_create(
                email=d['email'],
                defaults={
                    'created_by': user,
                    'name': d['name'],
                    'specialization': d['specialization'],
                    'phone': d['phone'],
                    'experience_years': d['experience_years']
                }
            )
            created_doctors.append(doc)

        # 3. Patients
        patients_data = [
            {
                'name': 'Eleanor Vance',
                'age': 42,
                'gender': 'Female',
                'phone': '+1 (555) 019-4820',
                'address': '742 Evergreen Terrace, Springfield',
                'medical_history': 'Type II Diabetes, regular glycemic monitoring.'
            },
            {
                'name': 'Marcus Thorne',
                'age': 58,
                'gender': 'Male',
                'phone': '+1 (555) 839-2041',
                'address': '1044 Beacon Street, Boston',
                'medical_history': 'Post-cardiac intervention follow-up. Aspirin regimen.'
            },
            {
                'name': 'Sophia Chen',
                'age': 29,
                'gender': 'Female',
                'phone': '+1 (555) 492-1189',
                'address': '55 Union Square, San Francisco',
                'medical_history': 'Mild seasonal asthma, albuterol PRN.'
            }
        ]

        created_patients = []
        for p in patients_data:
            pat, _ = Patient.objects.get_or_create(
                created_by=user,
                name=p['name'],
                defaults={
                    'age': p['age'],
                    'gender': p['gender'],
                    'phone': p['phone'],
                    'address': p['address'],
                    'medical_history': p['medical_history']
                }
            )
            created_patients.append(pat)

        # 4. Mappings
        if len(created_patients) >= 2 and len(created_doctors) >= 2:
            PatientDoctorMapping.objects.get_or_create(
                patient=created_patients[0],
                doctor=created_doctors[0],
                defaults={'assigned_by': user}
            )
            PatientDoctorMapping.objects.get_or_create(
                patient=created_patients[1],
                doctor=created_doctors[1],
                defaults={'assigned_by': user}
            )

        self.stdout.write(self.style.SUCCESS("CareOS demo dataset seeded successfully!"))
