from django.urls import path
from .views import *

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("",home_view,name="home"),
    path("create_entry/",create_entry_view,name="entry_create"),
    path("edit_entry/<int:entry_id>/",edit_entry_view,name="entry_edit"),
    path("driver/",driver_view,name="driver"),
    path("vehicle/",vehicle_view,name="vehicle"),
    path("entry/",entry_view,name="entry"),
    path("entry/<int:entry_id>/", entry_details_view, name="entry_details"),
    path("items/", items_view, name="items"),
    
    path("parties/", parties_view, name="parties"),
    path("parties/<int:party_id>/", party_details_view, name="party_details"),
    path('create-invoice/', create_invoice, name='create_invoice'),
    path('invoices/', invoices_view, name='invoices'),
    path('invoice/<int:invoice_id>/', display_invoice_view, name='invoice_details'),
]

# AJAX URLS
urlpatterns.extend([
    path('ajax/create-entry/', create_entry, name='ajax_create_entry'),
    path('ajax/edit-entry/', edit_entry_ajax, name='ajax_edit_entry'),
    path('ajax/delete-entry/', delete_entry_ajax, name='ajax_delete_entry'),
    path('ajax/create-vehicle/', create_vehicle, name='ajax_create_vehicle'),
    path('ajax/edit-vehicle/', edit_vehicle_ajax, name='ajax_edit_vehicle'),
    path('ajax/delete-vehicle/', delete_vehicle_ajax, name='ajax_delete_vehicle'),
    path('ajax/create-driver/', create_driver, name='ajax_create_driver'),
    path('ajax/delete-party/', delete_party_ajax, name='ajax_delete_party'),
    path('ajax/edit-party/', edit_party_ajax, name='ajax_edit_party'),
    path('ajax/delete-driver/', delete_driver_ajax, name='ajax_delete_driver'),
    path('ajax/edit-driver/', edit_driver_ajax, name='ajax_edit_driver'),
    path('ajax/create-party/', create_party, name='ajax_create_party'),
    path('ajax/create-item/', create_item, name='ajax_create_item'),
    path('ajax/edit-item/', edit_item_ajax, name='ajax_edit_item'),
    path('ajax/delete-item/', delete_item_ajax, name='ajax_delete_item'),
])

