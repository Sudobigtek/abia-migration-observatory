from django.contrib.auth import get_user_model
from django.test import TestCase

from .exceptions import DuplicateFieldError, ValidationError
from .models import (
    DynamicFieldDefinition,
    DynamicFieldValue,
    EntityDynamicData,
    EntityType,
    FieldType,
)
from .services import DynamicFieldService, FieldValidationService

User = get_user_model()


class FieldValidationServiceTests(TestCase):
    def setUp(self):
        self.defn = DynamicFieldDefinition(
            field_name="test_field",
            field_type=FieldType.TEXT,
            label="Test",
            max_length=10,
        )

    def test_validate_text_within_length(self):
        result = FieldValidationService.validate(self.defn, "hello")
        self.assertEqual(result, "hello")

    def test_validate_text_exceeds_length(self):
        with self.assertRaises(ValidationError):
            FieldValidationService.validate(self.defn, "hello world too long")

    def test_validate_choice(self):
        defn = DynamicFieldDefinition(
            field_name="status",
            field_type=FieldType.CHOICE,
            label="Status",
            choices=["active", "inactive"],
        )
        result = FieldValidationService.validate(defn, "active")
        self.assertEqual(result, "active")

    def test_validate_invalid_choice(self):
        defn = DynamicFieldDefinition(
            field_name="status",
            field_type=FieldType.CHOICE,
            label="Status",
            choices=["active", "inactive"],
        )
        with self.assertRaises(ValidationError):
            FieldValidationService.validate(defn, "unknown")

    def test_validate_number_range(self):
        defn = DynamicFieldDefinition(
            field_name="age",
            field_type=FieldType.INTEGER,
            label="Age",
            min_value=0,
            max_value=120,
        )
        result = FieldValidationService.validate(defn, 25)
        self.assertEqual(result, 25)

    def test_validate_number_out_of_range(self):
        defn = DynamicFieldDefinition(
            field_name="age",
            field_type=FieldType.INTEGER,
            label="Age",
            min_value=0,
            max_value=120,
        )
        with self.assertRaises(ValidationError):
            FieldValidationService.validate(defn, 150)

    def test_validate_boolean(self):
        defn = DynamicFieldDefinition(
            field_name="consent", field_type=FieldType.BOOLEAN, label="Consent"
        )
        self.assertTrue(FieldValidationService.validate(defn, True))
        self.assertTrue(FieldValidationService.validate(defn, "yes"))
        self.assertFalse(FieldValidationService.validate(defn, "no"))

    def test_validate_geojson(self):
        defn = DynamicFieldDefinition(
            field_name="location", field_type=FieldType.GEOJSON, label="Location"
        )
        geo = {"type": "Point", "coordinates": [7.5, 5.0]}
        result = FieldValidationService.validate(defn, geo)
        self.assertEqual(result["type"], "Point")

    def test_validate_invalid_geojson(self):
        defn = DynamicFieldDefinition(
            field_name="location", field_type=FieldType.GEOJSON, label="Location"
        )
        with self.assertRaises(ValidationError):
            FieldValidationService.validate(defn, {"type": "Invalid"})


class DynamicFieldServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin", email="admin@test.com", password="testpass123"
        )
        self.defn = DynamicFieldDefinition.objects.create(
            entity_type=EntityType.MIGRANT,
            field_name="displacement_cause",
            field_type=FieldType.CHOICE,
            label="Displacement Cause",
            choices=["conflict", "climate", "economic"],
            created_by=self.user,
        )

    def test_create_field_definition(self):
        data = {
            "entity_type": EntityType.MIGRANT,
            "field_name": "skills_match",
            "field_type": FieldType.TEXT,
            "label": "Skills Match",
        }
        result = DynamicFieldService.create_field_definition(data, self.user)
        self.assertEqual(result.field_name, "skills_match")

    def test_create_duplicate_field_raises(self):
        data = {
            "entity_type": EntityType.MIGRANT,
            "field_name": "displacement_cause",
            "field_type": FieldType.TEXT,
            "label": "Duplicate",
        }
        with self.assertRaises(DuplicateFieldError):
            DynamicFieldService.create_field_definition(data, self.user)

    def test_set_and_get_field_value(self):
        DynamicFieldService.set_field_value(
            self.defn, EntityType.MIGRANT, 1, "conflict", self.user
        )
        data = DynamicFieldService.get_entity_dynamic_data(
            EntityType.MIGRANT, 1)
        self.assertEqual(data["displacement_cause"], "conflict")

    def test_aggregate_rebuilds_on_save(self):
        DynamicFieldService.set_field_value(
            self.defn, EntityType.MIGRANT, 2, "climate", self.user
        )
        agg = EntityDynamicData.objects.get(
            entity_type=EntityType.MIGRANT, entity_id=2)
        self.assertEqual(agg.data["displacement_cause"], "climate")
        self.assertIn("climate", agg.search_vector)


class ODKFormGenerationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin", email="admin@test.com", password="testpass123"
        )
        DynamicFieldDefinition.objects.create(
            entity_type=EntityType.MIGRANT,
            field_name="full_name",
            field_type=FieldType.TEXT,
            label="Full Name",
            is_required=True,
            created_by=self.user,
        )
        DynamicFieldDefinition.objects.create(
            entity_type=EntityType.MIGRANT,
            field_name="gender",
            field_type=FieldType.CHOICE,
            label="Gender",
            choices=["male", "female", "other"],
            created_by=self.user,
        )

    def test_generate_odk_questions(self):
        from .services import ODKFormGenerationService

        questions = ODKFormGenerationService.generate_xlsform_questions(
            EntityType.MIGRANT
        )
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]["name"], "full_name")
        self.assertEqual(questions[0]["required"], "yes")
        self.assertIn("select_one", questions[1]["type"])
