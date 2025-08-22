frappe.ui.form.on("Case Master", {
    onload(frm) {
        const current_user_id = frappe.session.user;

        if (current_user_id) {
            frappe.db.get_value("User Details", { name: current_user_id }, ["user_email", "legal_team"])
                .then(response => {
                    const user_data = response.message;

                    if (user_data) {
                        const legal_team = user_data.legal_team;
                        const email = user_data.user_email;

                        if (legal_team) {
                            frm.set_value("legal_team", legal_team);
                            frm.set_value("email_address", user_email);
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
