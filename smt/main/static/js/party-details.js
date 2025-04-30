document.addEventListener('DOMContentLoaded', function() {
    const selectAllCheckbox = document.getElementById('select-all');
    const entryCheckboxes = document.querySelectorAll('.entry-checkbox:not(:disabled)');
    const createInvoiceBtn = document.getElementById('create-invoice-btn');
    const invoiceForm = document.getElementById('invoice-form');
    const modal = document.getElementById('invoice-modal');
    const closeModal = document.querySelector('.close-modal');
    const cancelModal = document.querySelector('.cancel-modal');
    const confirmInvoiceBtn = document.getElementById('confirm-invoice');
    const selectedEntriesBody = document.getElementById('selected-entries-body');
    const grandTotalElement = document.getElementById('grand-total');
    const selectionCounter = document.getElementById('selection-counter');
    
    // Filter elements
    const dateFilter = document.getElementById('date-filter');
    const vehicleFilter = document.getElementById('vehicle-filter');
    const driverFilter = document.getElementById('driver-filter');
    const applyFilterBtn = document.getElementById('apply-filter-btn');
    const resetFilterBtn = document.getElementById('reset-filter-btn');
    
    // Initialize Choices.js for vehicle and driver filters
    const vehicleChoices = new Choices(vehicleFilter, {
        removeItemButton: true,
        placeholder: true,
        placeholderValue: 'Select vehicles',
        searchPlaceholderValue: 'Search vehicles',
    });
    
    const driverChoices = new Choices(driverFilter, {
        removeItemButton: true,
        placeholder: true,
        placeholderValue: 'Select drivers',
        searchPlaceholderValue: 'Search drivers',
    });
    
    // Initialize flatpickr for date range filter
    const dateRangeFilter = flatpickr('#date-filter', {
        mode: 'range',
        dateFormat: 'd-m-Y',
        disableMobile: true,
        placeholder: 'Filter by date range',
        clear: true
    });
    
    // Initialize flatpickr for date range
    const dateRangePicker = flatpickr('#date-range', {
        mode: 'range',
        dateFormat: 'Y-m-d',
        disableMobile: true,
        defaultDate: [getFirstDayOfMonth(), getLastDayOfMonth()],
        onChange: function(selectedDates) {
            if (selectedDates.length === 2) {
                const fromDate = formatDate(selectedDates[0]);
                const toDate = formatDate(selectedDates[1]);
                
                document.getElementById('from-date').value = fromDate;
                document.getElementById('to-date').value = toDate;
            }
        }
    });
    
    // Helper function to get first day of current month
    function getFirstDayOfMonth() {
        const date = new Date();
        return new Date(date.getFullYear(), date.getMonth(), 1);
    }
    
    // Helper function to get last day of current month
    function getLastDayOfMonth() {
        const date = new Date();
        return new Date(date.getFullYear(), date.getMonth() + 1, 0);
    }
    
    // Helper function to format date to YYYY-MM-DD
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    // Helper function to parse date string in format DD-MM-YYYY
    function parseDate(dateStr) {
        if (!dateStr) return null;
        const [day, month, year] = dateStr.split('-').map(part => parseInt(part, 10));
        return new Date(year, month - 1, day);
    }
    
    // Set default values for hidden date inputs
    document.getElementById('from-date').value = formatDate(getFirstDayOfMonth());
    document.getElementById('to-date').value = formatDate(getLastDayOfMonth());
    
    // Handle "Select All" checkbox
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const visibleCheckboxes = document.querySelectorAll('tr:not(.hidden) .entry-checkbox:not(:disabled)');
            visibleCheckboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
            });
            updateCreateInvoiceButton();
            updateSelectionCounter();
        });
    }
    
    // Handle individual checkboxes
    entryCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSelectAllCheckbox();
            updateCreateInvoiceButton();
            updateSelectionCounter();
        });
    });
    
    // Update selection counter
    function updateSelectionCounter() {
        const selectedCount = document.querySelectorAll('.entry-checkbox:checked').length;
        selectionCounter.textContent = `${selectedCount} selected`;
        
        // Update visibility of counter
        if (selectedCount > 0) {
            selectionCounter.classList.add('has-selections');
        } else {
            selectionCounter.classList.remove('has-selections');
        }
    }
    
    // Apply filter button click handler
    if (applyFilterBtn) {
        applyFilterBtn.addEventListener('click', function() {
            // Deselect all checkboxes before applying filters
            const allCheckboxes = document.querySelectorAll('.entry-checkbox');
            allCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            
            // Reset the "Select All" checkbox
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = false;
            }
            
            applyFilters();
            updateSelectionCounter();
        });
    }
    
    // Reset filter button click handler
    if (resetFilterBtn) {
        resetFilterBtn.addEventListener('click', function() {
            resetFilters();
            updateSelectionCounter();
        });
    }
    
    // Apply filters to the table
    function applyFilters() {
        const dateRangeValue = dateFilter.value;
        let startDate = null;
        let endDate = null;
        
        if (dateRangeValue) {
            const dateRange = dateRangeValue.split(' to ');
            startDate = parseDate(dateRange[0]);
            endDate = dateRange.length > 1 ? parseDate(dateRange[1]) : startDate;
        }
        
        const selectedVehicles = vehicleChoices.getValue().map(item => item.value.trim().toLowerCase());
        const selectedDrivers = driverChoices.getValue().map(item => item.value.trim().toLowerCase());
        
        const rows = document.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            if (row.cells.length <= 1) return; // Skip "No entries found" row
            
            const dateCell = row.cells[1].textContent.trim();
            const vehicleCell = row.cells[4].textContent.trim().toLowerCase();
            const driverCell = row.cells[5].textContent.trim().toLowerCase();
            
            const rowDate = parseDate(dateCell);
            
            const dateMatch = !startDate || !rowDate || (rowDate >= startDate && rowDate <= endDate);
            const vehicleMatch = selectedVehicles.length === 0 || selectedVehicles.includes(vehicleCell);
            const driverMatch = selectedDrivers.length === 0 || selectedDrivers.includes(driverCell);
            
            if (dateMatch && vehicleMatch && driverMatch) {
                row.classList.remove('hidden');
            } else {
                row.classList.add('hidden');
            }
        });
        
        updateSelectAllCheckbox();
        updateCreateInvoiceButton();
        
        // Show filter applied indicator
        applyFilterBtn.classList.add('filter-applied');
    }
    
    // Reset all filters
    function resetFilters() {
        // Reset date range filter
        dateRangeFilter.clear();
        
        // Reset vehicle filter
        vehicleChoices.removeActiveItems();
        
        // Reset driver filter
        driverChoices.removeActiveItems();
        
        // Show all rows
        const rows = document.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.classList.remove('hidden');
        });
        
        // Reset filter applied indicator
        applyFilterBtn.classList.remove('filter-applied');
        
        updateSelectAllCheckbox();
        updateCreateInvoiceButton();
    }
    
    // Update "Create Invoice" button state
    function updateCreateInvoiceButton() {
        const visibleCheckboxes = document.querySelectorAll('tr:not(.hidden) .entry-checkbox:not(:disabled)');
        const hasCheckedEntries = Array.from(visibleCheckboxes).some(checkbox => checkbox.checked);
        createInvoiceBtn.disabled = !hasCheckedEntries;
    }
    
    // Update "Select All" checkbox state
    function updateSelectAllCheckbox() {
        const visibleCheckboxes = document.querySelectorAll('tr:not(.hidden) .entry-checkbox:not(:disabled)');
        
        if (visibleCheckboxes.length === 0) {
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = false;
            }
            return;
        }
        
        const allChecked = Array.from(visibleCheckboxes).every(checkbox => checkbox.checked);
        const someChecked = Array.from(visibleCheckboxes).some(checkbox => checkbox.checked);
        
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = allChecked;
            selectAllCheckbox.indeterminate = someChecked && !allChecked;
        }
    }
    
    // Open modal when Create Invoice button is clicked
    if (createInvoiceBtn) {
        createInvoiceBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Check if any entries are selected
            const selectedEntries = document.querySelectorAll('.entry-checkbox:checked').length;
            if (selectedEntries === 0) {
                Swal.fire({
                    title: 'No Entries Selected',
                    text: 'Please select at least one entry to create an invoice.',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
                return;
            }
            
            populateSelectedEntries();
            modal.style.display = 'block';
        });
    }
    
    // Close modal functions
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            confirmClose();
        });
    }
    
    if (cancelModal) {
        cancelModal.addEventListener('click', function() {
            confirmClose();
        });
    }
    
    // Function to confirm closing the modal
    function confirmClose() {
        // No changes detection needed anymore since we removed invoice number
        modal.style.display = 'none';
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            confirmClose();
        }
    });
    
    // Populate selected entries in the modal
    function populateSelectedEntries() {
        selectedEntriesBody.innerHTML = '';
        let grandTotal = 0;
        
        const checkedEntries = document.querySelectorAll('.entry-checkbox:checked');
        
        checkedEntries.forEach(checkbox => {
            const row = checkbox.closest('tr');
            const date = row.cells[1].textContent;
            const from = row.cells[2].textContent;
            const to = row.cells[3].textContent;
            const vehicle = row.cells[4].textContent;
            const total = parseFloat(row.cells[6].textContent);
            
            grandTotal += total;
            
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td>${date}</td>
                <td>${from}</td>
                <td>${to}</td>
                <td>${vehicle}</td>
                <td>₹ ${total.toFixed(2)}</td>
            `;
            selectedEntriesBody.appendChild(newRow);
        });
        
        grandTotalElement.textContent = `₹ ${grandTotal.toFixed(2)}`;
    }
    
    // Handle confirm invoice button
    if (confirmInvoiceBtn) {
        confirmInvoiceBtn.addEventListener('click', function() {
            const fromDate = document.getElementById('from-date').value;
            const toDate = document.getElementById('to-date').value;
            
            // Validate inputs with SweetAlert2
            if (!fromDate || !toDate) {
                Swal.fire({
                    title: 'Missing Information',
                    text: 'Please select a valid date range for the invoice',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
                return;
            }
            
            // Confirm invoice creation
            Swal.fire({
                title: 'Create Invoice?',
                html: `
                    <p>You are about to create an invoice with <strong>${document.querySelectorAll('.entry-checkbox:checked').length}</strong> entries.</p>
                    <p>Total Amount: <strong>${grandTotalElement.textContent}</strong></p>
                `,
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Create Invoice',
                cancelButtonText: 'Cancel',
                reverseButtons: true
            }).then((result) => {
                if (result.isConfirmed) {
                    // Show loading state
                    Swal.fire({
                        title: 'Creating Invoice...',
                        html: 'Please wait while we process your request.',
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();
                        }
                    });
                    
                    // Collect form data
                    const formData = new FormData(invoiceForm);
                    
                    formData.append('from_date', fromDate);
                    formData.append('to_date', toDate);
                    
                    // Convert FormData to JSON object
                    const data = {};
                    formData.forEach((value, key) => {
                        if (key === 'entry_ids') {
                            if (!data[key]) data[key] = [];
                            data[key].push(value);
                        } else {
                            data[key] = value;
                        }
                    });
                    
                    // Make AJAX request
                    fetch(invoiceForm.action, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            Swal.fire({
                                title: 'Success!',
                                text: 'Invoice created successfully.',
                                icon: 'success',
                                confirmButtonText: 'OK'
                            }).then(() => {
                                // Close modal
                                modal.style.display = 'none';
                                
                                // Disable the checkboxes and update their status
                                document.querySelectorAll('.entry-checkbox:checked').forEach(checkbox => {
                                    const row = checkbox.closest('tr');
                                    checkbox.checked = false;
                                    checkbox.disabled = true;
                                    
                                    // Update the invoiced status column
                                    const statusCell = row.cells[row.cells.length - 1];
                                    statusCell.innerHTML = `
                                        <span class="tag tag-invoiced">
                                            <span class="tag-dot"></span>
                                            Invoiced
                                        </span>
                                    `;
                                });
                                
                                // Update buttons state
                                updateSelectAllCheckbox();
                                updateCreateInvoiceButton();
                            });
                        } else {
                            Swal.fire({
                                title: 'Error!',
                                text: data.error || 'Failed to create invoice.',
                                icon: 'error',
                                confirmButtonText: 'OK'
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire({
                            title: 'Error!',
                            text: 'An unexpected error occurred. Please try again.',
                            icon: 'error',
                            confirmButtonText: 'OK'
                        });
                    });
                }
            });
        });
    }
    
    // Helper to add hidden input to form
    function addHiddenInput(name, value) {
        // Check if input already exists
        const existingInput = invoiceForm.querySelector(`input[name="${name}"]`);
        if (existingInput) {
            existingInput.value = value;
        } else {
            let input = document.createElement('input');
            input.type = 'hidden';
            input.name = name;
            input.value = value;
            invoiceForm.appendChild(input);
        }
    }
    
    // Initial updates
    updateSelectAllCheckbox();
    updateCreateInvoiceButton();
    updateSelectionCounter();
});
