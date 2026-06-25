# Aryan BusinessOS

**Industry ERP for Indian SMEs — built on ERPNext / Frappe**

Developed by [Aryan Consulting](https://aryanconsulting.in), Hyderabad.

---

## Modules

| Module | Status |
|---|---|
| Jewellery Manufacturing | ✅ v1.0 |
| Thermocole | ✅ v1.0 |
| Trading & Distribution | 🔜 Coming Soon |
| Retail / FMCG | 🔜 Coming Soon |

---

## Jewellery Manufacturing Module

Covers the full karigar (job work) accountability loop for gold, silver, and diamond jewellery manufacturers.

### Key DocTypes
- **Karigar** — Artisan master with per-metal acceptable loss thresholds
- **Job Work Challan** — Metal/stone issuance to karigar with auto WIP stock entry
- **Job Work Receipt** — Finished goods return with loss computation and alerts

### Features
- Weight-based inventory (grams, carats)
- Karigar WIP warehouse auto-creation
- Excess loss warnings with daily email alerts
- Overdue challan daily alerts
- Running karigar statistics (issued, returned, avg loss %)

---

## Thermocole Module

Covers in-house EPS thermocole manufacturing from production planning through shop-floor entry, quality inspection, and dispatch integration.

### Key DocTypes
- **Thermocole Mould** — Mould master with dimensions, bead grade, and run statistics
- **Thermocole Machine** — Pre-expander, block mould, shape mould, and cutting equipment registry
- **Thermocole Production Order** — Customer demand planning with dimensional specs
- **Thermocole Production Entry** — Shop-floor run with bead consumption, finished output, and yield tracking
- **Thermocole Quality Inspection** — Density, dimension, and visual QC with rejection handling

### Features
- Volume-based bead consumption estimates by density grade
- Manufacture Stock Entry integration on production submit
- Production order status lifecycle with overdue daily alerts
- ERPNext Item custom fields for default dimensions and mould linkage
- Delivery Note link field for dispatch traceability

---

## Installation

```bash
cd /path/to/frappe-bench
cp -r aryan_businessos apps/
echo "aryan_businessos" >> sites/apps.txt
bench --site yoursite.com install-app aryan_businessos
bench --site yoursite.com migrate
```

## Requirements

- Frappe >= 15.0.0
- ERPNext >= 15.0.0
- Python >= 3.10

---

## License

MIT — © 2026 Aryan Consulting
