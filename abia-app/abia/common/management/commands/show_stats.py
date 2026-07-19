from django.core.management.base import BaseCommand
from django.db.models import Count
from abia.accounts.models import User, LGA
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.referrals.models import Referral


class Command(BaseCommand):
    help = "Show platform statistics"

    def handle(self, *args, **options):
        self.stdout.write("=" * 50)
        self.stdout.write("ABIA MIGRATION OBSERVATORY — PLATFORM STATS")
        self.stdout.write("=" * 50)
        self.stdout.write(f"LGAs:              {LGA.objects.count()}")
        self.stdout.write(f"Users:             {User.objects.count()}")
        self.stdout.write(f"  by role:")
        for r in User.objects.values("role").annotate(c=Count("id")).order_by("role"):
            self.stdout.write(f"    {r['role']:20s} {r['c']}")
        self.stdout.write(f"Migrants:          {Migrant.objects.count()}")
        self.stdout.write(f"Cases:             {Case.objects.count()}")
        self.stdout.write(f"  by status:")
        for s in Case.objects.values("status").annotate(c=Count("id")).order_by("status"):
            self.stdout.write(f"    {s['status']:20s} {s['c']}")
        self.stdout.write(f"Referrals:         {Referral.objects.count()}")
        self.stdout.write(f"  by status:")
        for s in Referral.objects.values("status").annotate(c=Count("id")).order_by("status"):
            self.stdout.write(f"    {s['status']:20s} {s['c']}")
        self.stdout.write("=" * 50)
