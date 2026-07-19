from django.core.management.base import BaseCommand
from abia.accounts.services import UserService


class Command(BaseCommand):
    help = "Create a superuser with LGA assignment"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument("email", type=str)
        parser.add_argument("--password", type=str, required=True)
        parser.add_argument("--lga", type=str, help="LGA code (default: first LGA)")

    def handle(self, *args, **options):
        from abia.accounts.models import LGA
        lga_code = options.get("lga")
        lga = LGA.objects.filter(code=lga_code).first() if lga_code else LGA.objects.first()
        if not lga:
            self.stderr.write(self.style.ERROR("No LGA found. Run seed_lgas first."))
            return

        data = {
            "username": options["username"],
            "email": options["email"],
            "password": options["password"],
            "role": "super_admin",
            "lga": lga.id,
        }
        user = UserService.create(data, creator=None)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{user.username}' created with LGA '{lga.name}'"))
