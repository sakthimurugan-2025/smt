function filterParty() {
    const partySelect = document.getElementById('party-selection');
    const party = partySelect.options[partySelect.selectedIndex].value;
    if (party === 'all') {
        document.querySelectorAll("#table-body tr").forEach(row => {
            row.classList.remove("hide-party");
        });
        return;
    }
    document.querySelectorAll("#table-body tr").forEach(row => {
        row.classList.remove("hide-party");
        if (row.getAttribute("data-party") !== party) {
            row.classList.add("hide-party");
        }
    });
}

function filterVehicle() {
    const vehicleSelect = document.getElementById('vehicle-filter');
    const selectedOptions = Array.from(vehicleSelect.selectedOptions);
    const vehicles = selectedOptions.map(option => option.value);
    if (vehicles.length === 0) {
        document.querySelectorAll("#table-body tr").forEach(row => {
            row.classList.remove("hide-vehicle");
        });
        return;
    }
    document.querySelectorAll("#table-body tr").forEach(row => {
        row.classList.remove("hide-vehicle");
        if (!vehicles.includes(row.getAttribute("data-vehicle"))) {
            row.classList.add("hide-vehicle");
        }
    });
}

function filterDriver() {
    const driverSelect = document.getElementById('driver-filter');
    const selectedOptions = Array.from(driverSelect.selectedOptions);
    const drivers = selectedOptions.map(option => option.value);
    if (drivers.length === 0) {
        document.querySelectorAll("#table-body tr").forEach(row => {
            row.classList.remove("hide-driver");
        });
        return;
    }
    document.querySelectorAll("#table-body tr").forEach(row => {
        row.classList.remove("hide-driver");
        if (!drivers.includes(row.getAttribute("data-driver"))) {
            row.classList.add("hide-driver");
        }
    });
}

function filterDate() {
    const dateRangePicker = document.getElementById('date-range')._flatpickr;
    const selectedDates = dateRangePicker.selectedDates;
    if (selectedDates.length === 0) {
        document.querySelectorAll("#table-body tr").forEach(row => {
            row.classList.remove("hide-date");
        });
        return;
    }
    const [startDate, endDate] = selectedDates;
    document.querySelectorAll("#table-body tr").forEach(row => {
        row.classList.remove("hide-date");
        const rowDate = new Date(row.getAttribute("data-date"));
        if (rowDate < startDate || rowDate > endDate) {
            row.classList.add("hide-date");
        }
    });
}

function filterStatus() {
    const status = document.querySelector('input[name="status"]:checked').value;
    document.querySelectorAll("#table-body tr").forEach(row => {
        row.classList.remove("hide-invoice");
        const invoices = row.getAttribute("data-invoices");
        if (status === 'non-invoices' && parseInt(invoices)) {
            row.classList.add("hide-invoice");
        } else if (status === 'invoiced' && !parseInt(invoices)) {
            row.classList.add("hide-invoice");
        }
    });
}



// add event listener
document.getElementById('party-selection').addEventListener('change', filterParty);
document.getElementById('vehicle-filter').addEventListener('change', filterVehicle);
document.getElementById('driver-filter').addEventListener('change', filterDriver);
document.getElementById('date-range').addEventListener('change', filterDate);
document.querySelectorAll('input[name="status"]').forEach(radio => {
    radio.addEventListener('change', filterStatus);
});

// activate filter
filterDate()
filterParty()
filterVehicle()
filterDriver()
filterStatus()