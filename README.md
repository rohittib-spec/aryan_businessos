# Aryan BusinessOS

**Industry ERP for Indian SMEs — built on ERPNext / Frappe**

Developed by [Aryan Consulting](https://aryanconsulting.in), Hyderabad.

---

## Modules

| Module | Status |
|---|---|
| Jewellery Manufacturing | ✅ v1.0 |
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
