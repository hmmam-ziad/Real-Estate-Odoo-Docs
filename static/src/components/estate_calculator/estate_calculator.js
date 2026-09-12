// ------------------------------------------------------------
// Author      : HmMam Alsukhni
// Created     : 09-12-2026 | 10:21 PM (GMT+3)
// Module      : Estate
// File        : estate_calculator.js
// Purpose     : Defines the Estate Calculator OWL component and manages
//               property price, interest rate, payment period,
//               and monthly payment calculations.
// ------------------------------------------------------------

// Import the Component class and useState hook from OWL
import { Component, useState } from "@odoo/owl";

// Import Odoo's registry to register the custom field widget
import { registry } from "@web/core/registry";

// Create the Estate Calculator OWL component
export class EstateCalculator extends Component {

    // Define the XML template used by this component
    static template = "estate.EstateCalculator";

    setup() {
        // Create a reactive state for the calculator
        // The UI will automatically update when these values change
        this.state = useState({
            years: 10,          // Number of years for the payment plan
            interestRate: 5,   // Interest rate as a percentage
        });
    }

    // Calculate the monthly payment
    get monthlyPayment() {

        // Get the selling price if available.
        // Otherwise, use the expected price.
        // If neither exists, use 0.
        const price =
            this.props.record.data.selling_price ||
            this.props.record.data.expected_price ||
            0;

        // If the price is zero or negative, return 0
        if (!price || price <= 0) return 0;

        // Calculate the total interest
        // Example: 100,000 × 5% × 10 years
        const totalInterest =
            price * (this.state.interestRate / 100) * this.state.years;

        // Add the interest to the original property price
        const totalPrice = price + totalInterest;

        // Convert the number of years into months
        const totalMonths = this.state.years * 12;

        // Calculate and return the monthly payment
        // toFixed(2) keeps two decimal places
        return (totalPrice / totalMonths).toFixed(2);
    }

    // Called when the user changes the number of years
    onYearsChange(ev) {

        // Read the value from the input and convert it to an integer
        // If the value is invalid, use 1 year
        this.state.years = parseInt(ev.target.value) || 1;
    }
}

// Register the component as an Odoo field widget
// This allows it to be used with:
// widget="estate_calculator"
registry.category("fields").add("estate_calculator", {
    component: EstateCalculator,
});