import frappe
from frappe.utils import today


def alert_overdue_production_orders():
    """Daily task: notify manufacturing managers of overdue production orders."""
    overdue = frappe.db.sql(
        """
        SELECT name, customer, delivery_date, status
        FROM `tabThermocole Production Order`
        WHERE docstatus = 1
          AND status NOT IN ('Completed', 'Cancelled')
          AND delivery_date < %s
        """,
        today(),
        as_dict=True,
    )

    if not overdue:
        return

    rows = "".join(
        f"<tr><td>{r.name}</td><td>{r.customer or ''}</td>"
        f"<td>{r.delivery_date}</td><td>{r.status}</td></tr>"
        for r in overdue
    )

    message = f"""
    <p>The following Thermocole Production Orders are overdue:</p>
    <table border="1" cellpadding="4" cellspacing="0">
      <thead><tr>
        <th>Order</th><th>Customer</th><th>Delivery Date</th><th>Status</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """

    managers = frappe.db.sql(
        """
        SELECT DISTINCT u.email FROM `tabUser` u
        JOIN `tabHas Role` hr ON hr.parent = u.name
        WHERE hr.role IN ('Manufacturing Manager', 'Stock Manager') AND u.enabled = 1
        """,
        as_dict=True,
    )

    for mgr in managers:
        frappe.sendmail(
            recipients=[mgr.email],
            subject=f"[Aryan BusinessOS] {len(overdue)} Overdue Thermocole Production Order(s)",
            message=message,
        )
