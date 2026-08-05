
from django.test import TestCase
from .models import Beneficiary, PillarParticipation

class BeneficiaryModelTest(TestCase):
    def setUp(self):
        self.b = Beneficiary.objects.create(
            first_name="Test", last_name="User", phone="08012345678",
            date_of_birth="1990-01-01", gender="male", lga="Aba North"
        )

    def test_full_name(self):
        self.assertEqual(self.b.full_name, "Test User")

    def test_str(self):
        self.assertIn("Test User", str(self.b))

    def test_auto_pillars_created(self):
        self.assertEqual(self.b.pillar_participations.count(), 4)

class PillarParticipationTest(TestCase):
    def setUp(self):
        self.b = Beneficiary.objects.create(
            first_name="Chioma", last_name="Okonkwo", phone="08031234567",
            date_of_birth="1995-05-15", gender="female", lga="Aba South"
        )

    def test_completion_rate_p1(self):
        p1 = self.b.pillar_participations.get(pillar="p1")
        p1.total_counseling_sessions = 10
        p1.counseling_sessions_attended = 7
        p1.save()
        self.assertEqual(p1.completion_rate, 70.0)

    def test_unique_together(self):
        p1 = self.b.pillar_participations.get(pillar="p1")
        with self.assertRaises(Exception):
            PillarParticipation.objects.create(beneficiary=self.b, pillar="p1", enrolled_date="2026-01-01")
