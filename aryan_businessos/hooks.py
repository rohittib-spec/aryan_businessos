app_name = "aryan_businessos"
app_title = "Aryan BusinessOS"
app_publisher = "Aryan Consulting"
app_description = "Industry ERP for Indian SMEs — Jewellery Manufacturing"
app_email = "info@aryanconsulting.in"
app_license = "MIT"
app_version = "1.0.0"

# ------------------------------------------------------------------
# Modules
# ------------------------------------------------------------------
# app_include_css = "/assets/aryan_businessos/css/aryan_businessos.css"
# app_include_js = "/assets/aryan_businessos/js/aryan_businessos.js"

# ------------------------------------------------------------------
# Fixtures — pre-load masters on install
# ------------------------------------------------------------------
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Jewellery Manufacturing"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Jewellery Manufacturing"]]},
]

# ------------------------------------------------------------------
# Document Events
# ------------------------------------------------------------------
doc_events = {
    "Job Work Challan": {
        "on_submit": "aryan_businessos.jewellery_manufacturing.doctype.job_work_challan.job_work_challan.on_submit",
        "on_cancel": "aryan_businessos.jewellery_manufacturing.doctype.job_work_challan.job_work_challan.on_cancel",
    },
    "Job Work Receipt": {
        "on_submit": "aryan_businessos.jewellery_manufacturing.doctype.job_work_receipt.job_work_receipt.on_submit",
        "on_cancel": "aryan_businessos.jewellery_manufacturing.doctype.job_work_receipt.job_work_receipt.on_cancel",
    },
}

# ------------------------------------------------------------------
# Scheduled Tasks
# ------------------------------------------------------------------
scheduler_events = {
    "daily": [
        # Alert on overdue job work challans
        "aryan_businessos.jewellery_manufacturing.tasks.alert_overdue_challans",
        # Alert when karigar loss % exceeds threshold
        "aryan_businessos.jewellery_manufacturing.tasks.alert_karigar_excess_loss",
    ]
}

# ------------------------------------------------------------------
# Permissions
# ------------------------------------------------------------------
has_permission = {
    "Job Work Challan": "aryan_businessos.jewellery_manufacturing.doctype.job_work_challan.job_work_challan.has_permission",
    "Job Work Receipt": "aryan_businessos.jewellery_manufacturing.doctype.job_work_receipt.job_work_receipt.has_permission",
}

# ------------------------------------------------------------------
# Installation
# ------------------------------------------------------------------
after_install = "aryan_businessos.setup.after_install"
after_migrate = "aryan_businessos.setup.after_migrate"
