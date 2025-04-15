from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from django.shortcuts import redirect
import requests

def home_view(request):
    return render(request,"index.html")

def create_entry_view(request):

    return render(request,"create_entry.html",{
        "parties":Party.objects.all(),
        "vehicles":Vehicle.objects.all(),
        "drivers":Driver.objects.all(),
        "items":Item.objects.all()
    })

@csrf_exempt
def create_entry(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            # Parse date from DD-MM-YYYY format
            date_str = data['date']
            parsed_date = datetime.strptime(date_str, '%d-%m-%Y').date()
            
            party = Party.objects.get(id=data['party_id'])
            vehicle = Vehicle.objects.get(id=data['vehicle'])
            driver = Driver.objects.get(id=data['driver'])
            entry = Entry.objects.create(
                date=parsed_date,  # Use the parsed date
                customer_from=data['location_from'],
                customer_to=data['location_to'],
                party=party,
                vehicle=vehicle,
                driver=driver,
                total=sum(float(item['total']) for item in data['items'])
            )
            for item in data['items']:
                EntryItem.objects.create(
                    entry=entry,
                    item=Item.objects.get(id=item['id']),
                    quantity=item['quantity'],
                    total=item['total']
                )
            return JsonResponse({'success': True})
        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def driver_view(request):
    return render(request,"driver.html",{
        "drivers":Driver.objects.all()
    })

def vehicle_view(request):
    return render(request,"vehicle.html",{
        "vehicles": Vehicle.objects.all(),
        "companies": VehicleCompany.objects.all()  # Pass companies for the select dropdown
    })

def entry_view(request):
    entries = Entry.objects.all()
    parties = Party.objects.all()
    vehicles = Vehicle.objects.all()
    drivers = Driver.objects.all()
    
    if request.method == 'POST':
        data = request.POST
        print(data)

    return render(request, 'entry.html', {
        'entries': entries,
        'parties': parties,
        'vehicles': vehicles,
        'drivers': drivers
    })

def entry_details_view(request, entry_id):
    entry = Entry.objects.get(pk=entry_id)
    return render(request, "entry-details.html", {"entry": entry})

def delete_entry_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entry_id = data.get('id')
            entry = Entry.objects.get(id=entry_id)
            entry.delete()
            return JsonResponse({'success': True})
        except Entry.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Entry not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def parties_view(request):
    parties = Party.objects.all()
    return render(request,"parties.html",{
        "parties":parties
    })

def party_details_view(request, party_id):
    party = Party.objects.get(pk=party_id)
    entries = Entry.objects.filter(party=party).order_by('-date')
    
    return render(request, "party_details.html", {
        "party": party,
        "entries": entries,
        "vehicles": Vehicle.objects.all(),
        "drivers": Driver.objects.all(),
    })

@csrf_exempt
def create_vehicle(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            number = data.get('number')
            company_id = data.get('company_id')
            
            # Basic validation
            if not name:
                return JsonResponse({'success': False, 'error': 'Vehicle name is required'})
            
            # Create the vehicle
            vehicle = Vehicle(name=name, number=number)
            
            # Set company if provided
            if company_id:
                try:
                    company = VehicleCompany.objects.get(id=company_id)
                    vehicle.company = company
                except VehicleCompany.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Selected company does not exist'})
            
            vehicle.save()
            return JsonResponse({'success': True})
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def create_driver(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            phone = data.get('phone')
            
            # Basic validation
            if not name:
                return JsonResponse({'success': False, 'error': 'Driver name is required'})
            
            # Create the driver
            driver = Driver.objects.create(name=name, phone=phone)
            
            return JsonResponse({
                'success': True,
                'id': driver.id,
                'name': driver.name,
                'phone': driver.phone
            })
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def create_party(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            location = data.get('location')
            phone = data.get('phone')
            gst = data.get('gst')
            
            # Basic validation
            if not name:
                return JsonResponse({'success': False, 'error': 'Party name is required'})
            
            # Create the party
            party = Party.objects.create(name=name, location=location, phone=phone, gst=gst)
            
            return JsonResponse({'success': True, 'id': party.id, 'name': party.name})
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def create_invoice(request):
    if request.method == 'POST':
        # Check if this is an AJAX request (JSON content type)
        is_ajax = request.headers.get('Content-Type') == 'application/json'
        
        if is_ajax:
            try:
                data = json.loads(request.body)
                entry_ids = data.get('entry_ids', [])
                from_date = data.get('from_date')
                to_date = data.get('to_date')
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        else:
            # Traditional form submission
            entry_ids = request.POST.getlist('entry_ids')
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
        
        if not entry_ids or not from_date or not to_date:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Missing required data'})
            else:
                return JsonResponse({'success': False, 'error': 'Missing required data'})
        
        try:
            # Parse dates
            f_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            t_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            
            # Create invoice
            invoice = Invoice.objects.create(
                f_date=f_date,
                t_date=t_date
            )
            
                
            invoice.save()
            
            # Link entries to invoice
            party_id = None
            for entry_id in entry_ids:
                try:
                    entry = Entry.objects.get(id=entry_id)
                    InvoiceItem.objects.create(
                        entry=entry,
                        invoice=invoice
                    )
                    if not party_id:
                        party_id = entry.party.id
                except Entry.DoesNotExist:
                    continue
            
            if is_ajax:
                return JsonResponse({'success': True})
            
            # Redirect back to party details for traditional form submission
            if party_id:
                return redirect('party_details', party_id=party_id)
            return redirect('home')
        
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)})
            else:
                return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def invoices_view(request):
    invoices = Invoice.objects.all().order_by('-id')
    return render(request, "invoices.html", {
        "invoices": invoices
    })

def display_invoice_view(request, invoice_id):
    
    invoice = Invoice.objects.get(pk=invoice_id)
    items = invoice.invoiceitem_set.all()[::-1]
    # recalculate_all_totals_and_counts()
    
    return render(request, "invoice.html", {
        "invoice": invoice,
        "items": items,
    })

@csrf_exempt
def delete_party_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            party_id = data.get('id')
            party = Party.objects.get(id=party_id)
            party.delete()
            return JsonResponse({'success': True})
        except Party.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Party not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def edit_party_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            party_id = data.get('id')
            party = Party.objects.get(id=party_id)
            
            # Update party fields
            party.name = data.get('name', party.name)
            party.location = data.get('location', party.location)
            party.phone = data.get('phone', party.phone)
            party.gst = data.get('gst', party.gst)
            
            party.save()
            return JsonResponse({'success': True})
        except Party.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Party not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def delete_driver_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            driver_id = data.get('id')
            driver = Driver.objects.get(id=driver_id)
            driver.delete()
            return JsonResponse({'success': True})
        except Driver.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Driver not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def edit_driver_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            driver_id = data.get('id')
            driver = Driver.objects.get(id=driver_id)
            
            # Update driver fields
            driver.name = data.get('name', driver.name)
            driver.phone = data.get('phone', driver.phone)
            
            driver.save()
            return JsonResponse({'success': True})
        except Driver.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Driver not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def edit_vehicle_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            vehicle_id = data.get('id')
            vehicle = Vehicle.objects.get(id=vehicle_id)
            
            # Update vehicle fields
            vehicle.name = data.get('name', vehicle.name)
            vehicle.number = data.get('number', vehicle.number)
            company_id = data.get('company_id')
            
            if company_id:
                try:
                    company = VehicleCompany.objects.get(id=company_id)
                    vehicle.company = company
                except VehicleCompany.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Selected company does not exist'})
            else:
                vehicle.company = None
            
            vehicle.save()
            return JsonResponse({'success': True})
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def delete_vehicle_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            vehicle_id = data.get('id')
            vehicle = Vehicle.objects.get(id=vehicle_id)
            vehicle.delete()
            return JsonResponse({'success': True})
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def payment_view(request):
    parties = Party.objects.all()
    party_payments = []
    
    for party in parties:
        
        invoices = Invoice.objects.filter(party=party)
        

        total_invoiced = 0
        total_paid = 0
        
        for invoice in invoices:
            if invoice.total:
                total_invoiced += float(invoice.total)
            
            if invoice.paid:
                total_paid += float(invoice.paid)
        
        pending_amount = total_invoiced - total_paid
        
        
        party_payments.append({
            'party': party,
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'pending_amount': pending_amount
        })
    
    return render(request, "payment.html", {
        "parties": parties,
        "party_payments": party_payments
    })

def payment_details_view(request,party_id):
    party = Party.objects.get(pk=party_id)
    invoices = Invoice.objects.filter(party=party)
    total_invoiced = 0
    total_paid = 0
    
    for invoice in invoices:
        if invoice.total:
            total_invoiced += float(invoice.total)
        
        if invoice.paid:
            total_paid += float(invoice.paid)
    
    pending_amount = total_invoiced - total_paid

    payments = Payment.objects.filter(party=party)

    return render(request,"payment_details.html",{
        "party":party,
        "total":total_invoiced,
        "paid":total_paid,
        "pending":pending_amount,
        "payments":payments
    })

@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            party_id = data.get('party_id')
            amount = data.get('amount')
            
            # Basic validation
            if not party_id or not amount:
                return JsonResponse({'success': False, 'error': 'Missing required data'})
            
            try:
                party = Party.objects.get(id=party_id)
                payment_amount = float(amount)
                
                if payment_amount <= 0:
                    return JsonResponse({'success': False, 'error': 'Payment amount must be greater than zero'})
                
                # Create a new payment record
                payment = Payment.objects.create(
                    date=datetime.now().date(),
                    amount=str(payment_amount),
                    party=party,
                )
                
                # Update invoices starting from newest
                remaining_amount = payment_amount
                invoices = Invoice.objects.filter(party=party).order_by('-f_date')
                
                for invoice in invoices:
                    if remaining_amount <= 0:
                        break
                    
                    # Calculate pending amount for this invoice
                    invoice_total = float(invoice.total) if invoice.total else 0
                    invoice_paid = float(invoice.paid) if invoice.paid else 0
                    invoice_pending = invoice_total - invoice_paid
                    
                    if invoice_pending > 0:
                        # Determine amount to apply to this invoice
                        amount_to_apply = min(remaining_amount, invoice_pending)
                        invoice.paid = str(invoice_paid + amount_to_apply)
                        invoice.save()
                        
                        remaining_amount -= amount_to_apply
                
                return JsonResponse({
                    'success': True,
                    'message': f'Payment of ₹{payment_amount} processed successfully',
                    'payment': {
                        'id': payment.id,
                        'date': payment.date.strftime('%d-%m-%Y'),
                        'amount': payment.amount
                    }
                })
                
            except Party.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Party not found'})
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid amount format'})
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def backup_view(request):
        bot_api_key = "7218432904:AAH21pSYGFVTP4TCo9QjSu-3DeEkp317YdQ"
        user_id = "1612462958"

        def send_telegram_file(bot_api_key, user_id, file_path, caption=None):
            url = f"https://api.telegram.org/bot{bot_api_key}/sendDocument"
            with open(file_path, 'rb') as file:
                payload = {
                    "chat_id": user_id
                }
                if caption:
                    payload["caption"] = caption
                    
                files = {
                    "document": file
                }
                response = requests.post(url, data=payload, files=files)
            return response.json()

        try:
            # Fetch all data from the database
            parties = list(Party.objects.all().values())
            vehicles = list(Vehicle.objects.all().values())
            drivers = list(Driver.objects.all().values())
            entries = list(Entry.objects.all().values())
            items = list(Item.objects.all().values())
            invoices = list(Invoice.objects.all().values())
            payments = list(Payment.objects.all().values())

            # Combine all data into a single list of dictionaries for loaddata format
            data = []
            for model_name, objects in [
                ("app_name.party", parties),
                ("app_name.vehicle", vehicles),
                ("app_name.driver", drivers),
                ("app_name.entry", entries),
                ("app_name.item", items),
                ("app_name.invoice", invoices),
                ("app_name.payment", payments),
            ]:
                for obj in objects:
                    data.append({
                        "model": model_name,
                        "pk": obj["id"],
                        "fields": {k: v for k, v in obj.items() if k != "id"}
                    })

            # Convert data to JSON
            json_data = json.dumps(data, indent=4, default=str)

            # Save JSON data to a file
            file_path = "data.json"
            with open(file_path, "w") as file:
                file.write(json_data)

            # Send the file to Telegram
            send_telegram_file(bot_api_key, user_id, file_path)
            
            # Also send the static data_utf8.json file with the #file: prefix
            utf8_file_path = "d:\\PROGRAMMING\\SMT\\smt\\data_utf8.json"
            send_telegram_file(bot_api_key, user_id, utf8_file_path, caption="#file:data_utf8.json")

            return JsonResponse({'success': True, 'message': 'Backup files sent to Telegram successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

def edit_entry_view(request, entry_id):
    entry = Entry.objects.get(pk=entry_id)
    entry_items = EntryItem.objects.filter(entry=entry)
    parties = Party.objects.all()
    vehicles = Vehicle.objects.all()
    drivers = Driver.objects.all()
    all_items = Item.objects.all()
    
    return render(request, "edit_entry.html", {
        "entry": entry,
        "items": entry_items,
        "all_items": all_items,
        "parties": parties,
        "vehicles": vehicles,
        "drivers": drivers
    })

@csrf_exempt
def update_entry_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            entry_id = data['id']
            entry = Entry.objects.get(id=entry_id)
            
            # Parse date from DD-MM-YYYY format
            date_str = data['date']
            parsed_date = datetime.strptime(date_str, '%d-%m-%Y').date()
            
            # Update entry fields
            entry.date = parsed_date
            entry.customer_from = data['location_from']
            entry.customer_to = data['location_to']
            entry.party = Party.objects.get(id=data['party_id'])
            entry.vehicle = Vehicle.objects.get(id=data['vehicle'])
            entry.driver = Driver.objects.get(id=data['driver'])
            
            entry.save()
            
            # Handle items
            for item_data in data['items']:
                if item_data.get('deleted'):
                    # Delete item if it exists and is marked for deletion
                    if 'entry_item_id' in item_data:
                        try:
                            entry_item = EntryItem.objects.get(id=item_data['entry_item_id'])
                            entry_item.delete()
                        except EntryItem.DoesNotExist:
                            pass
                elif item_data.get('isNew'):
                    # Create new item
                    EntryItem.objects.create(
                        entry=entry,
                        item=Item.objects.get(id=item_data['id']),
                        quantity=item_data['quantity'],
                        total=item_data['total']
                    )
                elif 'entry_item_id' in item_data:
                    # Update existing item
                    entry_item = EntryItem.objects.get(id=item_data['entry_item_id'])
                    entry_item.item = Item.objects.get(id=item_data['id'])
                    entry_item.quantity = item_data['quantity']
                    entry_item.total = item_data['total']
                    entry_item.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})