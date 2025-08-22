frappe.ui.form.on("Hearing Details", {
    onload(frm) {
        // Get the current session user ID
        const current_user_id = frappe.session.user;

        if (current_user_id) {
            // Fetch the email address of the session user
            frappe.db.get_value("User", { name: current_user_id }, ["email", "group_email"])
                .then(response => {
                    const {email,group_email} = response.message;

                    if (email) {
                        // Set the value of custom_user with the email
                        frm.set_value("custom_user", email);
                        frm.set_df_property("custom_user", "read_only", 1);
                        // frm.set_df_property("email_address", "read_only", 1);

                    } else {
                        frappe.msgprint("Email address not found for the current user.");
                    }

                    if (group_email) {
                        frm.set_value("email_address",group_email);
                        frm.set_df_property("email_address", "read_only", 1)
                    }
                })
                .catch(error => {
                    console.error("Error fetching user email:", error);
                });
        } else {
            frappe.msgprint("Unable to fetch the current session user ID.");
        }
    }
});
