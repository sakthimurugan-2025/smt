import os
import django
import sys
from datetime import date

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smt.settings')
django.setup()

# Import models after Django setup
from main.models import Invoice, Payment

def add_payments():
    invoices = Invoice.objects.all()
    created_count = 0

    for invoice in invoices:
        # Skip if payment already exists for this invoice
        if Payment.objects.filter(invoice=invoice).exists():
            print(f'Payment already exists for invoice {invoice.id}')
            continue
            
        # Skip if invoice doesn't have a party
        if not invoice.party:
            print(f'Invoice {invoice.id} has no party, skipping')
            continue

        # Create payment record for this invoice
        payment = Payment(
            party=invoice.party,
            date=date.today(),
            pending_amount=invoice.total,
            received_amount="0",
            invoice=invoice
        )
        payment.save()
        created_count += 1
        print(f'Created payment for invoice {invoice.id}')

    print(f'Successfully created {created_count} payment records')

if __name__ == '__main__':
    add_payments()