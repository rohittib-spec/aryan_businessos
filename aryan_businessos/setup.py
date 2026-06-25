import frappe


def after_install():
    """Run after app is installed on a site."""
    create_jewellery_item_groups()
    create_metal_uom()
    frappe.db.commit()
    frappe.msgprint("Aryan BusinessOS — Jewellery Manufacturing module installed successfully.")


def after_migrate():
    """Run after every bench migrate."""
    pass


def create_jewellery_item_groups():
    """Create standard item groups for jewellery manufacturing."""
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
