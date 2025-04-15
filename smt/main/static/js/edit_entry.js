document.addEventListener('DOMContentLoaded', function() {
    // Initialize notifications
    const notyf = new Notyf({
        duration: 3000,
        position: { x: 'right', y: 'top' },
        types: [
            {
                type: 'success',
                background: '#28a745',
                duration: 3000,
                dismissible: true
            },
            {
                type: 'error',
                background: '#dc3545',
                duration: 4000,
                dismissible: true
            }
        ]
    });

    // Elements
    const totalDisplay = document.getElementById('total-display');
    const itemSelect = document.getElementById('item-select');
    const itemRateInput = document.getElementById('item-rate-inp');
    const itemQtyInput = document.getElementById('item-qty-inp');
    const itemTotalInput = document.getElementById('item-total-inp');
    const addRowBtn = document.getElementById('add-row-btn');
    const itemTableBody = document.getElementById('item-table-body');
    const updateEntryBtn = document.getElementById('update-entry');
    const entryId = document.getElementById('entry-id').value;
    const updateUrl = document.getElementById('update-url').value;
    const csrfToken = document.getElementById('csrf-token').value;
    
    // Item data storage
    let items = [];
    
    // Initialize items from existing rows
    const itemRows = document.querySelectorAll('.item-row');
    itemRows.forEach(row => {
        const itemId = row.dataset.itemId;
        const name = row.dataset.name;
        const quantity = row.dataset.quantity;
        const total = row.dataset.total;
        
        // Calculate rate (total / quantity)
        const rate = parseFloat(total) / parseFloat(quantity);
        
        items.push({
            id: itemId,
            entry_item_id: row.dataset.id,
            name: name,
            rate: rate.toFixed(2),
            quantity: quantity,
            total: total
        });
        
        // Add event listener to remove button
        const removeBtn = row.querySelector('.remove-item-btn');
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                removeItem(row, row.dataset.id);
            });
        }
    });
    
    // Update total display
    updateTotalDisplay();
    
    // Auto-calculate total when rate or quantity changes
    itemRateInput.addEventListener('input', calculateTotal);
    itemQtyInput.addEventListener('input', calculateTotal);
    
    // Calculate total based on rate and quantity
    function calculateTotal() {
        if (itemRateInput.value && itemQtyInput.value) {
            const rate = parseFloat(itemRateInput.value);
            const qty = parseFloat(itemQtyInput.value);
            if (!isNaN(rate) && !isNaN(qty)) {
                itemTotalInput.value = (rate * qty).toFixed(2);
            }
        }
    }
    
    // Add new item row
    addRowBtn.addEventListener('click', function() {
        if (itemSelect.value === 'NULL' || !itemRateInput.value || !itemQtyInput.value || !itemTotalInput.value) {
            notyf.error('Please fill in all item fields');
            return;
        }
        
        const itemId = itemSelect.value;
        const itemName = itemSelect.options[itemSelect.selectedIndex].text;
        const rate = parseFloat(itemRateInput.value);
        const quantity = itemQtyInput.value;
        const total = itemTotalInput.value;
        
        // Add item to array
        items.push({
            id: itemId,
            name: itemName,
            rate: rate.toFixed(2),
            quantity: quantity,
            total: total,
            isNew: true
        });
        
        // Add new row to table
        addItemRow(itemId, itemName, rate, quantity, total);
        
        // Clear inputs
        itemSelect.value = 'NULL';
        if (typeof SlimSelect !== 'undefined') {
            // Update SlimSelect if being used
            const slimSelect = document.querySelector('.ss-main');
            if (slimSelect && slimSelect.SlimSelect) {
                slimSelect.SlimSelect.set('NULL');
            }
        }
        itemRateInput.value = '';
        itemQtyInput.value = '';
        itemTotalInput.value = '';
        
        // Update total
        updateTotalDisplay();
    });
    
    // Add item row to table
    function addItemRow(itemId, name, rate, quantity, total, entryItemId = null) {
        const newRow = document.createElement('tr');
        newRow.className = 'item-row';
        newRow.dataset.itemId = itemId;
        if (entryItemId) {
            newRow.dataset.id = entryItemId;
        }
        
        newRow.innerHTML = `
            <td>${name}</td>
            <td>${rate}</td>
            <td>${quantity}</td>
            <th>${total}</th>
            <td><button class="remove-item-btn">X</button></td>
        `;
        
        itemTableBody.appendChild(newRow);
        
        // Add event listener to remove button
        const removeBtn = newRow.querySelector('.remove-item-btn');
        removeBtn.addEventListener('click', function() {
            removeItem(newRow, entryItemId);
        });
    }
    
    // Remove item from table and array
    function removeItem(row, entryItemId) {
        // Find index in items array
        let index;
        if (entryItemId) {
            index = items.findIndex(item => item.entry_item_id == entryItemId);
        } else {
            const itemId = row.dataset.itemId;
            const name = row.querySelector('td').textContent;
            index = items.findIndex(item => item.id == itemId && item.name === name);
        }
        
        if (index !== -1) {
            // If removing an existing item, mark it for deletion
            if (entryItemId && !items[index].isNew) {
                items[index].deleted = true;
            } else {
                // Remove from array if it's a new item
                items.splice(index, 1);
            }
        }
        
        // Remove row from table
        row.remove();
        
        // Update total
        updateTotalDisplay();
    }
    
    // Update total display
    function updateTotalDisplay() {
        let total = 0;
        items.forEach(item => {
            if (!item.deleted) {
                total += parseFloat(item.total);
            }
        });
        totalDisplay.textContent = total.toFixed(2);
    }
    
    // Update entry
    updateEntryBtn.addEventListener('click', function() {
        const partyId = document.getElementById('party-select').value;
        const locationFrom = document.getElementById('l_from').value;
        const locationTo = document.getElementById('l_to').value;
        const entryDate = document.getElementById('entry-date').value;
        const vehicleId = document.getElementById('vehicle-select').value;
        const driverId = document.getElementById('driver-select').value;
        
        // Validation
        if (partyId === 'NULL' || !locationFrom || !locationTo || !entryDate || vehicleId === 'NULL' || driverId === 'NULL') {
            notyf.error('Please fill in all required fields');
            return;
        }
        
        if (items.filter(item => !item.deleted).length === 0) {
            notyf.error('Please add at least one item');
            return;
        }
        
        // Prepare data for submission
        const data = {
            id: entryId,
            party_id: partyId,
            location_from: locationFrom,
            location_to: locationTo,
            date: entryDate,
            vehicle: vehicleId,
            driver: driverId,
            items: items
        };
        
        // Send update request
        fetch(updateUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                notyf.success('Entry updated successfully');
                // Redirect after a short delay
                setTimeout(() => {
                    window.location.href = `/entry/${entryId}/`;
                }, 1500);
            } else {
                notyf.error('Error: ' + (data.error || 'Failed to update entry'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            notyf.error('Error: ' + error.message);
        });
    });
});
