/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class EstateCalculator extends Component {
    static template = "estate.EstateCalculator"

    setup() {
        this.state = useState({
            years: 10,
            interestRate: 5,
        });
    }

    get monthlyPayment() {
        const price = this.props.record.data.selling_price || this.props.record.data.expected_price || 0;
        if (!price || price <= 0) return 0;

        const totalInterest = price * (this.state.interestRate / 100) * this.state.years;
        const totalPrice = price + totalInterest;
        const totalMonths = this.state.years * 12;

        return (totalPrice / totalMonths).toFixed(2);
    }

    onYearsChange(ev) {
        this.state.years = parseInt(ev.target.value) || 1;
    }
}

registry.category("fields").add("estate_calculator", {
    component: EstateCalculator,
});