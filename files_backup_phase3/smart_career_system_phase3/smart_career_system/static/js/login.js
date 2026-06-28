/* =====================================================
   login.js
   Handles client-side validation and submission
   for the Login page.
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const loginBtn = document.getElementById("loginBtn");

    loginForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        hideAlert();

        const loginIdentifier = document.getElementById("login_identifier").value.trim();
        const password = document.getElementById("password").value;

        let isValid = true;

        // ----- Validate login identifier -----
        if (loginIdentifier === "") {
            showFieldError("login_identifier", "Username or email is required.");
            isValid = false;
        } else {
            clearFieldError("login_identifier");
        }

        // ----- Validate password -----
        if (password === "") {
            showFieldError("password", "Password is required.");
            isValid = false;
        } else {
            clearFieldError("password");
        }

        if (!isValid) {
            return;
        }

        // ----- Submit to backend -----
        loginBtn.disabled = true;
        loginBtn.textContent = "Logging in...";

        try {
            const response = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    login_identifier: loginIdentifier,
                    password: password
                })
            });

            const result = await response.json();

            if (result.success) {
                showAlert(result.message, "success");
                setTimeout(() => {
                    window.location.href = result.redirect_url || "/dashboard";
                }, 800);
            } else {
                showAlert(result.message || "Login failed.", "error");
            }
        } catch (error) {
            console.error("Login error:", error);
            showAlert("Something went wrong. Please try again.", "error");
        } finally {
            loginBtn.disabled = false;
            loginBtn.textContent = "Log In";
        }
    });

    // Clear errors as user types
    document.getElementById("login_identifier").addEventListener("input", function () {
        clearFieldError("login_identifier");
    });
    document.getElementById("password").addEventListener("input", function () {
        clearFieldError("password");
    });
});
