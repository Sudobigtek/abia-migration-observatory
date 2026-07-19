from django.core.management.base import BaseCommand
from abia.accounts.models import LGA


LGAS = [
    {"name": "Aba North", "code": "AB-North"},
    {"name": "Aba South", "code": "AB-South"},
    {"name": "Arochukwu", "code": "AR"},
    {"name": "Bende", "code": "BE"},
    {"name": "Ikwuano", "code": "IK"},
    {"name": "Isiala Ngwa North", "code": "IN-North"},
    {"name": "Isiala Ngwa South", "code": "IN-South"},
    {"name": "Isuikwuato", "code": "IS"},
    {"name": "Obi Ngwa", "code": "ON"},
    {"name": "Ohafia", "code": "OH"},
    {"name": "Osisioma", "code": "OS"},
    {"name": "Ugwunagbo", "code": "UG"},
    {"name": "Ukwa East", "code": "UK-East"},
    {"name": "Ukwa West", "code": "UK-West"},
    {"name": "Umuahia North", "code": "UM-North"},
    {"name": "Umuahia South", "code": "UM-South"},
    {"name": "Umu Nneochi", "code": "UN"},
]


class Command(BaseCommand):
    help = "Seed the 17 Abia State LGAs"

    def handle(self, *args, **options):
        created = 0
        for data in LGAS:
            _, was_created = LGA.objects.get_or_create(
                code=data["code"],
                defaults={"name": data["name"]},
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Created {created} LGAs, {len(LGAS) - created} already existed"))
