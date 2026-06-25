import frappe


def after_install():
    """Run after app is installed on a site."""
    create_jewellery_item_groups()
    create_thermocole_item_groups()
    create_metal_uom()
    create_thermocole_uom()
    ensure_thermocole_custom_fields()
    frappe.db.commit()


def after_migrate():
    """Run after every bench migrate."""
    ensure_thermocole_custom_fields()
def create_jewellery_item_groups():
    """Create standard item groups for jewellery manufacturing."""
    if not frappe.db.exists("Item Group", "All Item Groups"):
        frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": "All Item Groups",
            "is_group": 1,
        }).insert(ignore_permissions=True)

    groups = [
        {"item_group_name": "Precious Metals", "parent_item_group": "All Item Groups"},
        {"item_group_name": "Gold", "parent_item_group": "Precious Metals"},
        {"item_group_name": "Silver", "parent_item_group": "Precious Metals"},
        {"item_group_name": "Diamonds & Stones", "parent_item_group": "All Item Groups"},
        {"item_group_name": "Finished Jewellery", "parent_item_group": "All Item Groups"},
        {"item_group_name": "Consumables", "parent_item_group": "All Item Groups"},
    ]
    for g in groups:
        if not frappe.db.exists("Item Group", g["item_group_name"]):
            doc = frappe.get_doc({"doctype": "Item Group", **g})
            doc.insert(ignore_permissions=True)


def create_metal_uom():
    """Ensure weight UOMs exist."""
    uoms = ["Gram", "Milligram", "Troy Ounce", "Carat", "Cent"]
    for uom in uoms:
        if not frappe.db.exists("UOM", uom):
            frappe.get_doc({"doctype": "UOM", "uom_name": uom}).insert(ignore_permissions=True)


def create_thermocole_item_groups():
    """Create standard item groups for thermocole manufacturing."""
    if not frappe.db.exists("Item Group", "All Item Groups"):
        frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": "All Item Groups",
            "is_group": 1,
        }).insert(ignore_permissions=True)

    groups = [
        {"item_group_name": "Thermocole", "parent_item_group": "All Item Groups", "is_group": 1},
        {"item_group_name": "EPS Raw Beads", "parent_item_group": "Thermocole"},
        {"item_group_name": "Pre-expanded Beads", "parent_item_group": "Thermocole"},
        {"item_group_name": "Finished Thermocole", "parent_item_group": "Thermocole"},
    ]
    for g in groups:
        if not frappe.db.exists("Item Group", g["item_group_name"]):
            doc = frappe.get_doc({"doctype": "Item Group", **g})
            doc.insert(ignore_permissions=True)


def create_thermocole_uom():
    """Ensure thermocole UOMs exist."""
    uoms = ["Kg", "Nos", "CBM"]
    for uom in uoms:
        if not frappe.db.exists("UOM", uom):
            frappe.get_doc({"doctype": "UOM", "uom_name": uom}).insert(ignore_permissions=True)


def ensure_thermocole_custom_fields():
    """Custom fields for thermocole manufacturing integration."""
    custom_fields = [
        {
            "dt": "Item",
            "fieldname": "custom_density_grade",
            "fieldtype": "Select",
            "options": "\nLow\nMedium\nHigh",
            "label": "Density Grade",
            "insert_after": "item_group",
            "module": "Thermocole",
        },
        {
            "dt": "Item",
            "fieldname": "custom_default_length_mm",
            "fieldtype": "Float",
            "label": "Default Length (mm)",
            "insert_after": "custom_density_grade",
            "module": "Thermocole",
        },
        {
            "dt": "Item",
            "fieldname": "custom_default_width_mm",
            "fieldtype": "Float",
            "label": "Default Width (mm)",
            "insert_after": "custom_default_length_mm",
            "module": "Thermocole",
        },
        {
            "dt": "Item",
            "fieldname": "custom_default_height_mm",
            "fieldtype": "Float",
            "label": "Default Height (mm)",
            "insert_after": "custom_default_width_mm",
            "module": "Thermocole",
        },
        {
            "dt": "Item",
            "fieldname": "custom_default_mould",
            "fieldtype": "Link",
            "options": "Thermocole Mould",
            "label": "Default Mould",
            "insert_after": "custom_default_height_mm",
            "module": "Thermocole",
        },
        {
            "dt": "Stock Entry",
            "fieldname": "custom_thermocole_production_entry",
            "fieldtype": "Link",
            "options": "Thermocole Production Entry",
            "label": "Thermocole Production Entry",
            "insert_after": "amended_from",
            "read_only": 1,
            "no_copy": 1,
            "module": "Thermocole",
        },
        {
            "dt": "Delivery Note",
            "fieldname": "custom_thermocole_production_order",
            "fieldtype": "Link",
            "options": "Thermocole Production Order",
            "label": "Thermocole Production Order",
            "insert_after": "customer",
            "read_only": 1,
            "no_copy": 1,
            "module": "Thermocole",
        },
    ]

    for field in custom_fields:
        name = f"{field['dt']}-{field['fieldname']}"
        if not frappe.db.exists("Custom Field", name):
            frappe.get_doc({"doctype": "Custom Field", **field}).insert(ignore_permissions=True)
