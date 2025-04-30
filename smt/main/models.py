from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Party(models.Model):
    name        = models.CharField(max_length=50)
    location    = models.CharField(max_length=50,null=True,blank=True)
    phone       = models.CharField(max_length=10,null=True,blank=True)
    gst         = models.CharField(max_length=15,null=True,blank=True)

    def __str__(self):
        return f"{self.name} - {self.location}"
    
class Driver(models.Model):
    name        = models.CharField(max_length=50)
    phone       = models.CharField(max_length=10,null=True,blank=True)
    
    def __str__(self):
        return f"{self.name}"

class VehicleCompany(models.Model):
    name        = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    name        = models.CharField(max_length=50)
    number      = models.CharField(max_length=10,null=True,blank=True)
    company     = models.ForeignKey(VehicleCompany,on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return f"{self.name} - {self.number}"

class Item(models.Model):
    name    = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Entry(models.Model):
    date    = models.DateField()
    customer_from   = models.CharField(max_length=100)
    customer_to     = models.CharField(max_length=100)
    party           = models.ForeignKey(Party,on_delete=models.CASCADE)
    vehicle         = models.ForeignKey(Vehicle,on_delete=models.SET_NULL,null=True)
    driver          = models.ForeignKey(Driver,on_delete=models.SET_NULL,null=True)
    total           = models.CharField(max_length=100,null=True,blank=True)
    no_of_invoices  = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.party.name} - {self.date} - {self.total}"
    
class EntryItem(models.Model):
    entry   = models.ForeignKey(Entry,on_delete=models.CASCADE)
    item    = models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity    = models.CharField(max_length=100)
    total = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.entry} - {self.item}"
    
class Invoice(models.Model):
    f_date = models.DateField()
    t_date = models.DateField()
    total = models.CharField(max_length=100,null=True,blank=True)
    paid = models.CharField(max_length=100,null=False,default="0")
    party = models.ForeignKey(Party,on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return F"{self.party} - {self.total}"

class InvoiceItem(models.Model):
    entry = models.ForeignKey(Entry,on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.entry} - {self.invoice}"


# Signal handlers for auto calculations
@receiver([post_save, post_delete], sender=EntryItem)
def update_entry_total(sender, instance, **kwargs):
    """Update the total field of an Entry when EntryItems are added/modified/deleted."""
    entry = instance.entry
    entry_items = EntryItem.objects.filter(entry=entry)
    
    if entry_items.exists():
        # Convert all totals to float for summation, then back to string
        try:
            total_sum = sum(float(item.total) for item in entry_items)
            entry.total = str(total_sum)
        except ValueError:
            # Handle case where total might not be a valid number
            entry.total = "Error in calculation"
    else:
        entry.total = "0"
    
    entry.save()

@receiver([post_save, post_delete], sender=InvoiceItem)
def update_entry_invoice_count(sender, instance, **kwargs):
    """Update the no_of_invoices field of an Entry when InvoiceItems are added/modified/deleted."""
    entry = instance.entry
    # Count distinct invoices linked to this entry
    invoice_count = InvoiceItem.objects.filter(entry=entry).values('invoice').distinct().count()
    entry.no_of_invoices = invoice_count
    entry.save()

@receiver([post_save, post_delete], sender=InvoiceItem)
def update_invoice_total(sender, instance, **kwargs):
    """Update the total field of an Invoice when InvoiceItems are added/modified/deleted."""
    invoice = instance.invoice
    # Get all entries linked to this invoice
    entry_ids = InvoiceItem.objects.filter(invoice=invoice).values_list('entry', flat=True)
    entries = Entry.objects.filter(id__in=entry_ids)
    
    if entries.exists():
        try:
            # Sum up all entry totals (convert to float for calculation)
            total_sum = sum(float(entry.total) for entry in entries if entry.total)
            invoice.total = str(total_sum)
        except ValueError:
            # Handle case where some entries might have invalid totals
            invoice.total = "Error in calculation"
    else:
        invoice.total = "0"
    
    invoice.save()

@receiver(post_save, sender=InvoiceItem)
def update_invoice_party(sender, instance, created, **kwargs):
    """Update the party field of an Invoice based on the first InvoiceItem's entry party."""
    invoice = instance.invoice
    
    # Only update if the party is not already set
    if not invoice.party:
        # Set the party from the InvoiceItem's entry
        invoice.party = instance.entry.party
        invoice.save(update_fields=['party'])

def recalculate_all_totals_and_counts():

    # Recalculate all entry totals
    for entry in Entry.objects.all():
        entry_items = EntryItem.objects.filter(entry=entry)
        if entry_items.exists():
            try:
                total_sum = sum(float(item.total) for item in entry_items)
                entry.total = str(total_sum)
            except ValueError:
                entry.total = "Error in calculation"
        else:
            entry.total = "0"
        
        # Also update invoice count while we're processing entries
        invoice_count = InvoiceItem.objects.filter(entry=entry).values('invoice').distinct().count()
        entry.no_of_invoices = invoice_count
        entry.save()
    
    # Recalculate all invoice totals
    for invoice in Invoice.objects.all():
        entry_ids = InvoiceItem.objects.filter(invoice=invoice).values_list('entry', flat=True)
        entries = Entry.objects.filter(id__in=entry_ids)
        
        if entries.exists():
            try:
                total_sum = sum(float(entry.total) for entry in entries if entry.total)
                invoice.total = str(total_sum)
            except ValueError:
                invoice.total = "Error in calculation"
        else:
            invoice.total = "0"
        
        invoice.save()
    
    return {
        'entries_updated': Entry.objects.count(),
        'invoices_updated': Invoice.objects.count()
    }

class Payment(models.Model):
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    date = models.DateField()
    pending_amount = models.CharField(max_length=100, null=True, blank=True)
    received_amount = models.CharField(max_length=100, null=True, blank=True)  
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.party} - Pending: {self.pending_amount}, Received: {self.received_amount} on {self.date}"

