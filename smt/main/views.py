from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from django.shortcuts import redirect

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
    
    # If not POST method
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def invoices_view(request):
    invoices = Invoice.objects.all().order_by('-f_date')  # Sort by date, newest first
    return render(request, "invoices.html", {
        "invoices": invoices
    })

def display_invoice_view(request, invoice_id):
    invoice = Invoice.objects.get(pk=invoice_id)
    items = InvoiceItem.objects.filter(invoice=invoice)
    
    recalculate_all_totals_and_counts()
    
    return render(request, "invoice.html", {
        "invoice": invoice,
        "items": items
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
        
        print()

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
