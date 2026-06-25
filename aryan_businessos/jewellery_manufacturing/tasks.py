import frappe
from frappe.utils import today, date_diff


def alert_overdue_challans():
    """Daily task: notify stock managers of overdue open challans."""
    overdue = frappe.db.sql("""
        SELECT name, karigar, expected_return_date, total_issued_weight
        FROM `tabJob Work Challan`
        WHERE docstatus = 1
          AND status IN ('Open', 'Partially Received')
          AND expected_return_date < %s
    """, today(), as_dict=True)

    if not overdue:
        return

    rows = "".join(
        f"<tr><td>{r.name}</td><td>{r.karigar}</td>"
        f"<td>{r.expected_return_date}</td><td>{r.total_issued_weight}g</td></tr>"
        for r in overdue
    )

    message = f"""
    <p>The following Job Work Challans are overdue:</p>
    <table border="1" cellpadding="4" cellspacing="0">
      <thead><tr>
        <th>Challan</th><th>Karigar</th><th>Expected Return</th><th>Issued Weight</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """

    # Notify all Stock Managers
    managers = frappe.db.sql("""
        SELECT DISTINCT u.email FROM `tabUser` u
        JOIN `tabHas Role` hr ON hr.parent = u.name
        WHERE hr.role = 'Stock Manager' AND u.enabled = 1
    """, as_dict=True)

    for mgr in managers:
        frappe.sendmail(
            recipients=[mgr.email],
            subject=f"[Aryan BusinessOS] {len(overdue)} Overdue Job Work Challan(s)",
            message=message
        )


def alert_karigar_excess_loss():
    """Daily task: flag karigar accounts with excess average loss."""
    excess = frappe.db.sql("""
        SELECT name, karigar_name, avg_loss_pct
        FROM `tabKarigar`
        WHERE status = 'Active'
          AND avg_loss_pct > 0
    """, as_dict=True)

    # Compare against threshold — simplified: flag anyone over 5% as a starting heuristic
    GLOBAL_THRESHOLD = 5.0
    flagged = [k for k in excess if k.avg_loss_pct > GLOBAL_THRESHOLD]

    if not flagged:
        return

    rows = "".join(
        f"<tr><td>{k.karigar_name}</td><td>{k.avg_loss_pct}%</td></tr>"
        for k in flagged
    )

    message = f"""
    <p>The following Karigar accounts have average metal loss above {GLOBAL_THRESHOLD}%:</p>
    <table border="1" cellpadding="4" cellspacing="0">
      <thead><tr><th>Karigar</th><th>Avg Loss %</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <p>Please review their Job Work Receipts.</p>
    """

    managers = frappe.db.sql("""
        SELECT DISTINCT u.email FROM `tabUser` u
        JOIN `tabHas Role` hr ON hr.parent = u.name
        WHERE hr.role = 'Stock Manager' AND u.enabled = 1
    """, as_dict=True)

    for mgr in managers:
        frappe.sendmail(
            recipients=[mgr.email],
            subject="[Aryan BusinessOS] Karigar Excess Loss Alert",
            message=message
        )
