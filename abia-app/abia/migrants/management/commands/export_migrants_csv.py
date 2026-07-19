import csv
import sys
from django.core.management.base import BaseCommand
from abia.migrants.repositories import MigrantRepository


class Command(BaseCommand):
    help = "Export migrants to CSV (stdout or file)"

    def add_arguments(self, parser):
        parser.add_argument("--lga", type=str, help="Filter by LGA code")
        parser.add_argument("--status", type=str, help="Filter by status")
        parser.add_argument("--output", type=str, default="-", help="Output file (default: stdout)")

    def handle(self, *args, **options):
        qs = MigrantRepository.get_all()
        if options.get("lga"):
            from abia.accounts.models import LGA
            lga = LGA.objects.filter(code=options["lga"]).first()
            if lga:
                qs = MigrantRepository.get_by_lga(lga.id)
        if options.get("status"):
            qs = qs.filter(status=options["status"])

        out = sys.stdout if options["output"] == "-" else open(options["output"], "w", newline="")
        writer = csv.writer(out)
        writer.writerow(["id", "full_name", "phone", "gender", "current_lga", "status", "created_at"])
        for m in qs:
            writer.writerow([m.id, m.full_name, m.phone, m.gender, m.current_lga.name if m.current_lga else "", m.status, m.created_at])
        if out is not sys.stdout:
            out.close()
            self.stdout.write(self.style.SUCCESS(f"Exported {qs.count()} migrants to {options['output']}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Exported {qs.count()} migrants"))
