import frappe
from frappe import _
from frappe.utils import flt

from aryan_businessos.thermocole.utils.warehouse import get_wip_warehouse


def create_production_stock_entry(production_entry):
    """Create a Manufacture Stock Entry from a submitted Thermocole Production Entry."""
    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Manufacture"
    se.purpose = "Manufacture"
    se.posting_date = production_entry.entry_date
    if frappe.get_meta("Stock Entry").has_field("custom_thermocole_production_entry"):
        se.custom_thermocole_production_entry = production_entry.name

    wip_warehouse = get_wip_warehouse()

    for row in production_entry.materials or []:
        if not flt(row.actual_qty):
            continue
        se.append(
            "items",
            {
                "item_code": row.item_code,
                "qty": flt(row.actual_qty),
                "uom": row.uom or "Kg",
                "s_warehouse": row.warehouse,
                "t_warehouse": wip_warehouse,
            },
        )

    for row in production_entry.outputs or []:
        if not flt(row.qty):
            continue
        se.append(
            "items",
            {
                "item_code": row.item_code,
                "qty": flt(row.qty),
                "uom": row.uom or "Nos",
                "s_warehouse": wip_warehouse,
                "t_warehouse": row.warehouse,
                "is_finished_item": 1,
            },
        )

    if not se.items:
        frappe.throw(_("Add material and output rows before submitting the Production Entry."))

    try:
        se.insert(ignore_permissions=True)
        se.submit()
    except Exception as exc:
        frappe.throw(_("Could not create Stock Entry for this production entry: {0}").format(str(exc)))

    return se


def create_rejection_stock_entry(production_entry, rejected_qty, item_code, source_warehouse):
    """Move rejected quantity to the rejection warehouse."""
    if not flt(rejected_qty):
        return None

    from aryan_businessos.thermocole.utils.warehouse import get_rejection_warehouse

    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Material Transfer"
    se.purpose = "Material Transfer"
    se.posting_date = production_entry.entry_date
    if frappe.get_meta("Stock Entry").has_field("custom_thermocole_production_entry"):
        se.custom_thermocole_production_entry = production_entry.name

    se.append(
        "items",
        {
            "item_code": item_code,
            "qty": flt(rejected_qty),
            "uom": "Nos",
            "s_warehouse": source_warehouse,
            "t_warehouse": get_rejection_warehouse(),
        },
    )

    se.insert(ignore_permissions=True)
    se.submit()
    return se
