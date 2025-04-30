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
            total_amount = 0
            for entry_id in entry_ids:
                try:
                    entry = Entry.objects.get(id=entry_id)
                    InvoiceItem.objects.create(
                        entry=entry,
                        invoice=invoice
                    )
                    if not party_id:
                        party_id = entry.party.id
                    
                    # Add to total amount if entry.total is a valid number
                    if entry.total:
                        try:
                            total_amount += float(entry.total)
                        except (ValueError, TypeError):
                            pass
                            
                except Entry.DoesNotExist:
                    continue
            
            # Set the party for the invoice
            if party_id:
                party = Party.objects.get(id=party_id)
                invoice.party = party
                invoice.save()
                
                # Create a payment record for this invoice with the pending amount
                # and the current date
                Payment.objects.create(
                    party=party,
                    date=datetime.now().date(),
                    pending_amount=str(total_amount),
                    received_amount="0",
                    invoice=invoice
                )
            
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
    
    # Get the party from the first invoice item's entry (if items exist)
    party = None
    if items and len(items) > 0:
        party = items[0].entry.party
    
    return render(request, "invoice.html", {
        "invoice": invoice,
        "items": items,
        "party": party,
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
    # Get all parties
    parties = Party.objects.all()
    parties_with_balances = []
    
    # Calculate balance for each party based only on Payment model
    for party in parties:
        # Get all payments for this party
        payments = Payment.objects.filter(party=party)
        
        credit_sum = 0
        debit_sum = 0
        
        for payment in payments:
            # Add pending amount to credit_sum
            if payment.pending_amount:
                try:
                    credit_sum += float(payment.pending_amount)
                except (ValueError, TypeError):
                    # Handle case where pending_amount might not be a valid number
                    pass
            
            # Add received amount to debit_sum
            if payment.received_amount:
                try:
                    debit_sum += float(payment.received_amount)
                except (ValueError, TypeError):
                    # Handle case where received_amount might not be a valid number
                    pass
        
        # Calculate balance
        balance = credit_sum - debit_sum
        
        # Add computed values to party object
        party.credit_sum = "{:.2f}".format(credit_sum)
        party.debit_sum = "{:.2f}".format(debit_sum)
        party.balance = balance
        
        parties_with_balances.append(party)
    
    return render(request, "payment.html", {
        "parties": parties_with_balances
    })

def payment_details_view(request, party_id):
    """View for displaying and managing payment details for a specific party."""
    try:
        party = Party.objects.get(pk=party_id)
        payments = Payment.objects.filter(party=party).order_by('-date')
        
        # Calculate balance summary
        credit_sum = 0
        debit_sum = 0
        
        for payment in payments:
            # Add pending amount to credit_sum
            if payment.pending_amount:
                try:
                    credit_sum += float(payment.pending_amount)
                except (ValueError, TypeError):
                    pass
            
            # Add received amount to debit_sum
            if payment.received_amount:
                try:
                    debit_sum += float(payment.received_amount)
                except (ValueError, TypeError):
                    pass
        
        balance = credit_sum - debit_sum
        
        # Get related invoices for this party
        invoices = Invoice.objects.filter(party=party).order_by('-id')
        
        return render(request, "payment_details.html", {
            "party": party,
            "payments": payments,
            "credit_sum": "{:.2f}".format(credit_sum),
            "debit_sum": "{:.2f}".format(debit_sum),
            "balance": balance,
            "invoices": invoices
        })
        
    except Party.DoesNotExist:
        return redirect('payment')

@csrf_exempt
def create_payment_ajax(request):
    """AJAX endpoint for creating new payment records."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            party_id = data.get('party_id')
            payment_date = data.get('date')
            pending_amount = data.get('pending_amount', '0')
            received_amount = data.get('received_amount', '0')
            invoice_id = data.get('invoice_id')
            
            # Basic validation
            if not party_id or not payment_date:
                return JsonResponse({'success': False, 'error': 'Party and date are required'})
            
            # Format amounts correctly
            if pending_amount == '':
                pending_amount = '0'
            if received_amount == '':
                received_amount = '0'
            
            # Get objects
            party = Party.objects.get(pk=party_id)
            invoice = None
            if invoice_id:
                try:
                    invoice = Invoice.objects.get(pk=invoice_id)
                except Invoice.DoesNotExist:
                    pass
            
            # Parse date
            try:
                payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid date format'})
            
            # Create the payment
            payment = Payment.objects.create(
                party=party,
                date=payment_date,
                pending_amount=pending_amount,
                received_amount=received_amount,
                invoice=invoice
            )
            
            return JsonResponse({
                'success': True, 
                'id': payment.id,
                'date': payment.date.strftime('%Y-%m-%d'),
                'pending_amount': payment.pending_amount,
                'received_amount': payment.received_amount,
                'invoice_id': payment.invoice.id if payment.invoice else None
            })
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Party.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Party not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def delete_payment_ajax(request):
    """AJAX endpoint for deleting payment records."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_id = data.get('id')
            
            if not payment_id:
                return JsonResponse({'success': False, 'error': 'Payment ID is required'})
            
            payment = Payment.objects.get(pk=payment_id)
            payment.delete()
            
            return JsonResponse({'success': True})
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Payment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Payment not found'})
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
            # payments = list(Payment.objects.all().values())

            # Combine all data into a single list of dictionaries for loaddata format
            data = []
            for model_name, objects in [
                ("app_name.party", parties),
                ("app_name.vehicle", vehicles),
                ("app_name.driver", drivers),
                ("app_name.entry", entries),
                ("app_name.item", items),
                ("app_name.invoice", invoices),
                # ("app_name.payment", payments),
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

def items_view(request):
    items = Item.objects.all()
    return render(request, "items.html", {
        "items": items
    })

@csrf_exempt
def create_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            
            # Basic validation
            if not name:
                return JsonResponse({'success': False, 'error': 'Item name is required'})
            
            # Create the item
            item = Item.objects.create(name=name)
            
            return JsonResponse({'success': True, 'id': item.id, 'name': item.name})
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def delete_item_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('id')
            item = Item.objects.get(id=item_id)
            item.delete()
            return JsonResponse({'success': True})
        except Item.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def edit_item_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('id')
            item = Item.objects.get(id=item_id)
            
            # Update item fields
            item.name = data.get('name', item.name)
            
            item.save()
            return JsonResponse({'success': True})
        except Item.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

