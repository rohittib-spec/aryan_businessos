import frappe
from frappe import _

from aryan_businessos.jewellery_manufacturing.utils.warehouse import get_company_root_warehouse


def get_default_company(company=None):
    company = company or frappe.defaults.get_user_default("Company")
    if not company:
        frappe.throw(_("Please set a default Company."))
    return company


def get_or_create_thermocole_warehouse(label, warehouse_type="Stores", company=None):
    """Return a named thermocole warehouse, creating it under the company root if needed."""
    company = get_default_company(company)
    abbr = frappe.db.get_value("Company", company, "abbr")
    warehouse_name = f"{label} - {abbr}"

    if frappe.db.exists("Warehouse", warehouse_name):
        return warehouse_name

    parent_warehouse = get_company_root_warehouse(company)
    wh = frappe.get_doc(
        {
            "doctype": "Warehouse",
            "warehouse_name": label,
            "warehouse_type": warehouse_type,
            "company": company,
            "parent_warehouse": parent_warehouse,
        }
    )
    wh.insert(ignore_permissions=True)
    return warehouse_name


def get_wip_warehouse(company=None):
    return get_or_create_thermocole_warehouse("Thermocole WIP", "Work In Progress", company)


def get_finished_goods_warehouse(company=None):
    return get_or_create_thermocole_warehouse("Thermocole Finished Goods", "Stores", company)


def get_rejection_warehouse(company=None):
    return get_or_create_thermocole_warehouse("Thermocole Rejection", "Stores", company)
