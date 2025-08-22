import frappe
from frappe.utils import cstr, getdate
from datetime import datetime


@frappe.whitelist()
def get_hearing_dates(start=None, end=None):
    try:
        # Debugging: Log received parameters
        print(f"Received parameters - start: {start}, end: {end}")

        # Ensure start and end are valid dates
        if not start or not end:
            frappe.throw("Missing required date parameters: start and end")

        try:
            start_date = getdate(start)
            end_date = getdate(end)
        except Exception as e:
            frappe.throw(f"Invalid date format: {start}, {end}")

        print(f"Fetching hearings from {start_date} to {end_date}")

        # Query the database for hearing dates
        hearing_dates = frappe.db.sql("""
            SELECT 
                hdt.name AS event_id,
                hdt.hearing_date AS start_date,
                hdt.hearing_date AS end_date,
                hdt.hearing_details_link
            FROM `tabHearing Date` hdt
            WHERE hdt.hearing_date BETWEEN %(start)s AND %(end)s
        """, {"start": start_date, "end": end_date}, as_dict=True)


        events = []
        for hearing in hearing_dates:
            hearing_details_link = hearing.get("hearing_details_link")
            title = "No Title"

            if isinstance(hearing_details_link, str):
                title = frappe.db.get_value("Hearing Details", hearing_details_link, "title") or "No Title"

            events.append({
                "doctype": "Hearing Date",
                "name": hearing.get("event_id"),
                "title": title,  
                "start": hearing.get("start_date"),  
                "end": hearing.get("end_date"),
            })


        return events
    except Exception as e:
        frappe.log_error(f"Error in get_hearing_dates: {str(e)}", "Hearing Dates Error")
        return []
