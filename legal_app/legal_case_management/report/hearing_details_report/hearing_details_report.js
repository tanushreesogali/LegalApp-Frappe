frappe.query_reports["Hearing Details Report"] = {
	"filters": [
        {
            "fieldname": "legal_team",
            "label": __("Legal Team"),
            "fieldtype": "Select",
            "options": [
                { "label": "IP", "value": "IP" },
                { "label": "Legal", "value": "Legal" }
            ],
            "default": null,
            "reqd": 0,
            "hidden": 1
        },
		{
            "fieldname": "opposite_party",
            "label": __("Opposite Party"),
            "fieldtype": "Data",
            "default": null,
            "reqd": 0
        },
        {
            "fieldname": "case_number",
            "label": __("Case Number"),
            "fieldtype": "Link",
            "options": "Case Master",
            "reqd": 0
        },
		{
            "fieldname": "case_status",
            "label": __("Case Status"),
            "fieldtype": "Select",
            "options": [
                { "label": "Open", "value": "Open" },
                { "label": "Closed", "value": "Closed" },
                { "label": "Re-Open", "value": "Re-Open" }
            ],
            "default": null,
            "reqd": 0
        },
        {
            "fieldname": "filing_year",
            "label": __("Year"),
            "fieldtype": "Int",
            "default": null,
            "reqd": 0
        },
        {
            "fieldname": "lawyer_name",
            "label": __("Lawyer Name"),
            "fieldtype": "Link",
            "options": "Lawyer Master",
            "reqd": 0
        }

	]
};
