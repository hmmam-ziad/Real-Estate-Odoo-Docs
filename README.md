<div align="center">

# 🏠 Real Estate Management Module (`estate`)
### Odoo 19 — Enterprise / Community

![Odoo Version](https://img.shields.io/badge/Odoo-19.0-purple.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-LGPL--3-green.svg)

</div>

A comprehensive, production-ready **Real Estate Management** custom module built for **Odoo 19**, following official Odoo developer best practices and architectural patterns.

This module encapsulates core real estate operations including property listing, buyer-seller negotiations, offer lifecycle management, UI enhancements, constraint validation, automated invoicing, and module-to-module interaction.

---

## 🛠️ Key Features & Technical Highlights

### 1. Core Property Management
- **Property Lifecycle:** Full status tracking (`New` ➔ `Offer Received` ➔ `Offer Accepted` ➔ `Sold` / `Canceled`).
- **Categorization & Tagging:** Dynamic categorization with property types and colored tags (`widget="many2many_tags"`).
- **Computed Fields & Onchanges:** Automatic evaluation of best offer, selling price logic, and dynamic UI updates (e.g., auto-setting price percent and garden specs).

### 2. Business Logic & Automated Invoicing
- **Offer Accept/Refuse Workflow:** Accepting an offer automatically updates the property's selling price, links the buyer, and cancels redundant offers.
- **Accounting Integration (`account.move`):** Selling a property automatically generates a draft customer invoice including a 6% commission fee and fixed administrative costs, using the modern Odoo 19 `Command.create()` syntax.
- **Strict Validation (`UserError` & `ValidationError`):** Prevents selling canceled properties or accepting offers below 90% of the expected price.

### 3. Advanced UI/UX & Views
- **Header Action Buttons:** Primary and secondary status triggers (`Sold`, `Cancel`) with contextual visibility (`invisible`).
- **Smart Buttons (`statinfo`):** Interactive counter buttons displaying total active offers linked to specific properties.
- **QWeb Kanban View:** Interactive Kanban board grouped by Property Type, with conditional QWeb logic (`t-if`) to render dynamic price chips.
- **Inline Editable Views:** `One2many` table modifications directly inside the main form view (`editable="bottom"`).

### 4. Database Integrity & Constraints
- **SQL Constraints (`_sql_constraints`):** DB-level enforcement of positive expected/selling prices and unique property type/tag names.
- **Python Constraints (`@api.constrains`):** Backend logic to enforce price limits using standard float helpers (`float_compare`, `float_is_zero`).

### 5. Architectural Inheritance
- **Model Extension (`_inherit`):** Seamlessly extended `res.partner` to embed a dedicated **Real Estate Properties** tab showcasing properties acquired by a specific contact.
- **XPath View Inheritance:** Clean injection of custom XML UI elements into standard Odoo base forms without modifying core files.

---

## 🏗️ Module Architecture & Data Model

```text
estate/
├── models/
│   ├── estate_property.py          # Main property model & invoice triggering
│   ├── estate_property_type.py     # Property categories & computed property counts
│   ├── estate_property_tag.py      # Colored tags for property grouping
│   ├── estate_property_offer.py    # Offer validation & acceptance logic
│   └── res_partner.py              # Extended contact model with buyer properties
├── views/
│   ├── estate_property_views.xml   # Form, List, Kanban views & Smart Buttons
│   ├── estate_property_type_views.xml
│   ├── estate_property_tag_views.xml
│   ├── estate_property_offer_views.xml
│   ├── res_partner_views.xml       # XPath inheritance views for Contacts
│   └── estate_menus.xml            # Top-level menu structure
├── security/
│   └── ir.model.access.csv         # ACL security permissions
├── __manifest__.py                 # Dependencies (base, account) & data manifests
└── __init__.py
```

---

## 🚀 Installation & Usage Guide

### Prerequisites
- Odoo 19 (Community or Enterprise edition)
- Python 3.10+
- PostgreSQL database server

### Step 1: Clone the Repository

Navigate to your Odoo `custom_addons` directory and clone the repository:

```bash
cd /path/to/your/odoo/custom_addons
git clone https://github.com/hmmam-ziad/Real-Estate-Odoo-Docs.git estate
```

### Step 2: Configure Odoo

Ensure your `odoo.conf` file includes the path to your custom addons folder:

```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/your/custom_addons
```

### Step 3: Install the Module

Start your Odoo server instance with the module initialization/update flag:

```bash
./odoo-bin -c /path/to/odoo.conf -u estate -d your_database_name
```

Alternatively, log into Odoo as an Administrator:

1. Activate Developer Mode (**Settings ➔ Activate Developer Mode**).
2. Navigate to **Apps**.
3. Click **Update Apps List**.
4. Search for **Real Estate (estate)** and click **Activate / Install**.

### Step 4: Practical Usage Walkthrough

**1. Create Property Types & Tags**
- Go to **Real Estate ➔ Settings ➔ Property Types** (e.g., Residential, Commercial).
- Go to **Real Estate ➔ Settings ➔ Property Tags** and assign visual color badges (e.g., Cozy, Renovated, Garage).

**2. Add a Property Listing**
- Navigate to **Real Estate ➔ Properties ➔ Create**.
- Fill in expected price, available date, bedrooms, and garden details.

**3. Manage Customer Offers**
- In the **Offers** tab inside a property form, buyers can submit bid amounts.
- Click the ✔ (Accept) icon next to an offer.
- **Outcome:** The property state updates to `Offer Accepted`, the selling price locks, and the buyer is linked automatically.

**4. Sell & Auto-Generate Invoice**
- Click the **Sold** button in the top action header.
- **Outcome:** The property converts to `Sold`, and an automatic draft Customer Invoice is generated under **Accounting / Invoicing** containing the property commission line items.

---

## 📜 License

This project is licensed under the **LGPL-3** License.
