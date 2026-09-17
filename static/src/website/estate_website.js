/** @odoo-module **/

function initEstateOfferForm() {
    const form = document.getElementById("estate_offer_form");
    if (!form) return;

    console.log("Estate Offer Form Initialized!");

    const feedback = document.getElementById("estate_offer_feedback");
    const container = document.querySelector("[data-property-id]");
    const propertyId = container ? container.getAttribute("data-property-id") : null;

    function showFeedback(message, isError) {
        feedback.textContent = message;
        feedback.classList.remove("d-none", "alert-success", "alert-danger");
        feedback.classList.add(isError ? "alert-danger" : "alert-success");
    }

    form.addEventListener("submit", async function (ev) {
        ev.preventDefault();

        const submitBtn = form.querySelector("button[type='submit']");
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin me-1"></i> Submitting...';

        const formData = new FormData(form);
        const payload = {
            property_id: propertyId,
            price: formData.get("price"),
            partner_name: formData.get("partner_name"),
            partner_email: formData.get("partner_email"),
        };

        try {
            const response = await fetch("/api/v1/property/offer", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: payload,
                }),
            });
            const data = await response.json();
            const result = data.result || {};

            if (result.status === "success") {
                showFeedback(result.message || "Offer submitted!", false);
                form.reset();
            } else {
                showFeedback(result.message || "Something went wrong. Please try again.", true);
            }
        } catch (err) {
            showFeedback("Network error. Please check your connection and try again.", true);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa fa-handshake-o me-1"></i> Make an Offer';
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initEstateOfferForm);
} else {
    initEstateOfferForm();
}