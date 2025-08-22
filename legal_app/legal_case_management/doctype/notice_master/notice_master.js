frappe.ui.form.on("Notice Master", {
    onload(frm) {
        // Get the current session user ID
        const current_user_id = frappe.session.user;

        if (current_user_id) {
            // Fetch the legal_team from the User Doctype
            frappe.db.get_value("User", { name: current_user_id }, ["legal_team"])
                .then(response => {
                    const user_data = response.message;

                    if (user_data) {
                        const legal_team = user_data.legal_team;

                        if (legal_team) {
                            // Set the value of legal_team in the Notice Master Doctype
                            frm.set_value("legal_team", legal_team);
                            frm.set_df_property("legal_team", "read_only", 1);
                        } else {
                            frappe.msgprint("No legal team assigned to the current user.");
                        }
                    } else {
                        frappe.msgprint("User data not found.");
                    }
                })
                .catch(error => {
                    console.error("Error fetching user data:", error);
                });
        } else {
            frappe.msgprint("Unable to fetch the current session user ID.");
        }
    }
});
