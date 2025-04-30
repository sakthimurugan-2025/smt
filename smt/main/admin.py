from django.contrib import admin
from .models import *

class EntryItemInline(admin.TabularInline):
    model = EntryItem

class EntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'party', 'customer_from', 'customer_to', 'total', 'no_of_invoices')
    inlines = [EntryItemInline]

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('date', 'party', 'pending_amount', 'received_amount', 'invoice')

admin.site.register(Entry, EntryAdmin)
admin.site.register(EntryItem)
admin.site.register(Item)
admin.site.register(Vehicle)
admin.site.register(Driver)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Party)
admin.site.register(Payment, PaymentAdmin)