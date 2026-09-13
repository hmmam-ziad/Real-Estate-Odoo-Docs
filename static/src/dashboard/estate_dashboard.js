import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";


export class EstateDashboard extends Component {
    static template = "estate.EstateDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            totalProperties: 0,
            soldProperties: 0,
            totalRevenue: 0,
            recentOffers: [],
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        this.state.totalProperties = await this.orm.searchCount("estate.property", []);

        this.state.soldProperties = await this.orm.searchCount("estate.property", [
            ["state", "=", "sold"],
        ]);

        const soldProperties = await this.orm.searchRead(
            "estate.property",
            [["state", "=", "sold"]],
            ["selling_price"]
        );
        this.state.totalRevenue = soldProperties.reduce((sum, p) => sum + (p.selling_price || 0), 0);

        this.state.recentOffers = await this.orm.searchRead(
            "estate.property.offer",
            [],
            ["price", "partner_id", "property_id", "status"],
            { limit: 5, order: "id desc" }
        );
    }

    openProperties(domain, title) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: title,
            res_model: "estate.property",
            views: [[false, "list"], [false, "form"]],
            domain: domain,
        });
    }
}

registry.category("actions").add("estate_dashboard_tag", EstateDashboard);