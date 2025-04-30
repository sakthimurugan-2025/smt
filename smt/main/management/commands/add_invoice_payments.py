from django.core.management.base import BaseCommand
from main.models import Invoice, Payment
from django.utils import timezone

class Command(BaseCommand):
    help = 'Add payment row for every invoice in the database'

    def handle(self, *args, **options):
        invoices = Invoice.objects.all()
        created_count = 0

        for invoice in invoices:
            # Skip if payment already exists for this invoice
            if Payment.objects.filter(invoice=invoice).exists():
                self.stdout.write(self.style.WARNING(f'Payment already exists for invoice {invoice.id}'))
                continue

            # Create payment record for this invoice
            payment = Payment(
                party=invoice.party,
                date=timezone.now().date(),
                pending_amount=invoice.total,
                received_amount="0",
                invoice=invoice
            )
            payment.save()
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'Created payment for invoice {invoice.id}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} payment records'))