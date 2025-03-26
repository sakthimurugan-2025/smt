const Item_Rate_Inp = document.getElementById("item-rate-inp");
const Item_Qty_Inp = document.getElementById("item-qty-inp");
const Item_Total_Inp = document.getElementById("item-total-inp");

const TOAST = new Notyf({
    duration: 3000,
    position: {
        x: 'right',
        y: 'bottom',
    }
});

// Load existing items on page load
document.addEventListener("DOMContentLoaded", function() {
    // Get entry items from global variable defined in the HTML template
    if (typeof entryItems !== 'undefined' && Array.isArray(entryItems)) {
        // Add existing items to the table
        entryItems.forEach(item => {
            addRow(item.name, item.id, item.quantity, item.rate, item.total);
        });
        
        calculateTotal();
    }
});

document.getElementById("add-row-btn").addEventListener("click", function () {
    const itemType = document.getElementById("item-select").value;
    const itemTypeName = document.querySelector("#item-select").selectedOptions[0].dataset.name;
    if (itemType === "NULL" || itemType === "NaN") {
        TOAST.error("Select an item")
        return;
    }
    const rate = document.getElementById("item-rate-inp").value;
    if (rate === "" || rate === "NaN") {
        TOAST.error("Enter Rate Field or Total")
        return;
    }
    const qty = document.getElementById("item-qty-inp").value;
    if (qty === "" || qty === "NaN") {
        TOAST.error("Enter Quantity Field")
        return;
    }

    const total = document.getElementById("item-total-inp").value;
    if (total === "" || total === "NaN") {
        TOAST.error("Enter Rate Field or Total")
        return;
    }

    addRow(itemTypeName, itemType, qty, rate, total)
    Item_Rate_Inp.value = "";
    Item_Qty_Inp.value = "";
    Item_Total_Inp.value = "";
    calculateTotal();
});

function addRow(name, type, qty, rate, total) {
    const tr = document.createElement("tr");
    tr.classList.add("item-row");

    const td1 = document.createElement("td");
    td1.textContent = name;
    td1.setAttribute("data-type", type);
    td1.setAttribute("data-qty", qty);
    td1.setAttribute("data-rate", rate);
    td1.setAttribute("data-total", total);

    const td2 = document.createElement("td");
    td2.textContent = rate;

    const td3 = document.createElement("td");
    td3.textContent = qty;

    const th = document.createElement("th");
    th.textContent = total;

    const td4 = document.createElement("td");
    const button = document.createElement("button");

    button.addEventListener("click", () => {
        tr.remove();
        calculateTotal();
    });

    button.textContent = "X";
    td4.appendChild(button);

    tr.appendChild(td1);
    tr.appendChild(td2);
    tr.appendChild(td3);
    tr.appendChild(th);
    tr.appendChild(td4);
    document.getElementById("item-table-body").append(tr);
}

// ADD_ROW_RATE
Item_Rate_Inp.addEventListener("input", function () {
    this.value = this.value.replace(/[^0-9.]/g, ''); // Remove non-numeric characters except '.'
    if ((this.value.match(/\./g) || []).length > 1) {
        this.value = this.value.slice(0, -1); // Prevent multiple dots
    }
    if (this.value && Item_Qty_Inp.value) {
        Item_Total_Inp.value = (parseFloat(this.value) * parseFloat(Item_Qty_Inp.value)).toFixed(2);
    }
});

// ADD_ROW_TOTAL
Item_Total_Inp.addEventListener("input", function () {
    this.value = this.value.replace(/[^0-9.]/g, ''); // Remove non-numeric characters except '.'
    if ((this.value.match(/\./g) || []).length > 1) {
        this.value = this.value.slice(0, -1); // Prevent multiple dots
    }
    if (this.value && Item_Qty_Inp.value && parseFloat(Item_Qty_Inp.value) > 0) {
        Item_Rate_Inp.value = (parseFloat(this.value) / parseFloat(Item_Qty_Inp.value)).toFixed(2);
    }
});

// ADD_ROW_QTY
Item_Qty_Inp.addEventListener("input", function () {
    this.value = this.value.replace(/[^0-9.]/g, ''); // Remove non-numeric characters except '.'
    if ((this.value.match(/\./g) || []).length > 1) {
        this.value = this.value.slice(0, -1); // Prevent multiple dots
    }
    if (this.value && Item_Rate_Inp.value) {
        Item_Total_Inp.value = (parseFloat(this.value) * parseFloat(Item_Rate_Inp.value)).toFixed(2);
    }
});

function calculateTotal() {
    let sum = 0;
    document.querySelectorAll(".item-row td:first-child").forEach(function(row) {
        sum += parseFloat(row.dataset.total);
    });
    document.getElementById("total-display").innerHTML = sum.toFixed(2);
}

function triggerShakeEffect(id) {
    let element = document.getElementById(id);
    element.classList.add("shake");
    setTimeout(() => {
        element.classList.remove("shake");
    }, 3000);
}

function showModal(message, success = false) {
    const modal = document.getElementById("modal");
    const modalMessage = document.getElementById("modal-message");
    const modalButtons = document.getElementById("modal-buttons");

    modalMessage.textContent = message;
    
    // Clear any existing image
    const existingImg = document.getElementById("success-gif");
    if (existingImg) existingImg.remove();
    
    // Add image for success case
    if (success) {
        const successImg = document.createElement("img");
        successImg.id = "success-gif";
        successImg.src = "https://i.pinimg.com/originals/4a/10/e3/4a10e39ee8325a06daf00881ac321b2f.gif";
        successImg.alt = "Success";
        successImg.style.maxWidth = "100%";
        successImg.style.marginBottom = "20px";
        successImg.style.borderRadius = "8px";
        
        // Insert the image before the message
        modalMessage.parentNode.insertBefore(successImg, modalMessage);
        
        // Clear the buttons container
        modalButtons.innerHTML = '';
        
        // For success case, automatically redirect after 2 seconds
        const entryId = document.getElementById("entry-id").value;
        setTimeout(() => {
            window.location.href = `/entry/${entryId}/`;
        }, 2000);
    } else {
        // Only show close button for error case
        modalButtons.innerHTML = `<button id="close-btn">Close</button>`;
        document.getElementById("close-btn").addEventListener("click", () => {
            modal.style.display = "none";
        });
    }

    modal.style.display = "block";
}

document.getElementById("update-entry").addEventListener("click", function() {
    const party_id = document.getElementById("party-select").value;
    if(party_id === "NULL" || party_id === "" || party_id === null) {
        TOAST.error("Select The Party");
        document.getElementById("party-sec").scrollIntoView({ behavior: "smooth" });
        triggerShakeEffect("party-sec");
        return;
    }

    const location_from = document.getElementById("l_from").value;
    if (location_from === "") {
        TOAST.error("Enter the FROM location");
        document.getElementById("location-sec").scrollIntoView({ behavior: "smooth" });
        triggerShakeEffect("location-sec");
        return;
    } else if (location_from.length < 3) {
        TOAST.error("FROM Location must be at least 3 characters long");
        document.getElementById("location-sec").scrollIntoView({ behavior: "smooth" });
        triggerShakeEffect("location-sec");
        return;
    }

    const location_to = document.getElementById("l_to").value;
    if (location_to === "") {
        TOAST.error("Enter the TO location");
        document.getElementById("location-sec").scrollIntoView({ behavior: "smooth" });
        triggerShakeEffect("location-sec");
        return;
    } else if (location_to.length < 3) {
        TOAST.error("TO Location must be at least 3 characters long");
        document.getElementById("location-sec").scrollIntoView({ behavior: "smooth" });
        triggerShakeEffect("location-sec");
        return;
    }
    
    const date = document.getElementById("entry-date").value;
    if (date === "") {
        TOAST.error("Choose the date");
        document.getElementById("date-sec").scrollIntoView({ behavior: "smooth" });
        triggerShakeEffect("date-sec");
        return;
    }

    const vehicle_id = document.getElementById("vehicle-select").value;
    if(vehicle_id === "NULL" || vehicle_id === "" || vehicle_id === null) {
        TOAST.error("Select a vehicle");
        document.getElementById("vehicle-sec").scrollIntoView({ behavior: "smooth" });
        triggerShakeEffect("vehicle-sec");
        return;
    }
    
    const driver_id = document.getElementById("driver-select").value;
    if(driver_id === "NULL" || driver_id === "" || driver_id === null) {
        TOAST.error("Select a driver");
        document.getElementById("vehicle-sec").scrollIntoView({ behavior: "smooth" });
        triggerShakeEffect("vehicle-sec");
        return;
    }

    const rows = document.querySelectorAll("#item-table-body .item-row td:first-child");
    let items = [];
    if (rows.length > 0) {
        rows.forEach(row => {
            items.push({
                "id": row.dataset.type,
                "quantity": row.dataset.qty,
                "rate": row.dataset.rate,
                "total": row.dataset.total
            });
        });
    } else {
        TOAST.error("Add at least one item");
        document.getElementById("item-sec").scrollIntoView({ behavior: "smooth" });
        triggerShakeEffect("item-sec");
        return;
    }
    
    const entry_id = document.getElementById("entry-id").value;
    
    const formData = {
        "entry_id": entry_id,
        "party_id": party_id,
        "location_from": location_from,
        "location_to": location_to,
        "date": date,
        "vehicle": vehicle_id,
        "driver": driver_id,
        "items": items
    };
    
    const URL = document.getElementById('post-url').value;
    const csrfToken = document.getElementById('crsf').value;
    
    if(this.disabled){
        TOAST.error("Please wait for the previous request to complete");
        return;
    }
    this.disabled = true;

    fetch(URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            TOAST.success("Entry updated successfully");
            showModal("Entry updated successfully", true);
        } else {
            TOAST.error("Error updating entry: " + (data.error || "Unknown error"));
            showModal("Error updating entry: " + (data.error || "Unknown error"));
        }
        document.getElementById("update-entry").disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        TOAST.error("Error updating entry");
        showModal("Error updating entry");
        document.getElementById("update-entry").disabled = false;
    });
});
