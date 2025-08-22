import frappe

def execute(filters=None):

    user_id = frappe.session.user
    user_doc = frappe.get_doc("User", user_id)
    legal_team_value = user_doc.legal_team if hasattr(user_doc, "legal_team") else None  

    if filters and legal_team_value:
        filters["legal_team"] = legal_team_value

    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    # Define the columns for the report
    column_order = [
        "name", "case_no", "status", "filing_date", "hearing_date", 
        "details_of_hearing", "opposite_party", "case_stage", "court_name", "lawyer"
    ]
    
    columns = []
    
    # Adding columns dynamically
    for field in column_order:
        columns.append({
            "label": field.replace("_", " ").title(),
            "fieldname": field,
            "fieldtype": "Data",
            "width": 200
        })
    
    return columns

def get_data(filters):
    # Base SQL query to get hearing details along with its child data
    query = """
        SELECT
        	hd.name,
            hd.case_no,
            cm.case_number,
            cm.status,
            cm.filing_date,
            STRING_AGG(DISTINCT hdt.hearing_date::TEXT, E'\n\n') AS hearing_date,
            STRING_AGG(DISTINCT hdt.details_of_hearing, E'\n\n') AS details_of_hearing,
            cm.opposite_party,
            cm.case_stage,
            cm.court_name,
            lm.name AS lawyer
        FROM
            `tabHearing Details` hd
        LEFT JOIN
            `tabCase Master` cm ON hd.case_no = cm.name
        LEFT JOIN
            `tabLawyer Master` lm ON cm.lawyer_name = lm.name
        LEFT JOIN
            `tabHearing Details Data` hdt ON hd.name = hdt.parent
        WHERE
            1 = 1
    """
    
    # Add dynamic filtering based on user input
    conditions = []
    if filters.get("case_no"):
        conditions.append("cm.name = %(case_number)s")
    if filters.get("status"):
        conditions.append("cm.status = %(status)s")
    if filters.get("lawyer_name"):
        conditions.append("cm.lawyer_name = %(lawyer_name)s")
    if filters.get("filing_year"):
        conditions.append("EXTRACT(YEAR FROM cm.filing_date) = %(filing_year)s")
    if filters.get("opposite_party"):
        conditions.append("cm.opposite_party LIKE %(opposite_party)s")
        filters["opposite_party"] = f"%{filters['opposite_party']}%"
    if filters.get("legal_team"):
        conditions.append("cm.legal_team = %(legal_team)s")
    
    # Apply conditions if any
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    query += """
        GROUP BY
            hd.name, cm.case_number, cm.status, cm.filing_date,
            cm.opposite_party, cm.case_stage, cm.court_name, lm.name
    """
    
    # Execute the SQL query with filters
    data = frappe.db.sql(query, filters, as_dict=True)
    return data
