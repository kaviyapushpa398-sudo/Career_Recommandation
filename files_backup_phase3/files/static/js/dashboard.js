/* =====================================================
   dashboard.js
   Handles the logout action on the dashboard page.
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const logoutBtn = document.getElementById("logoutBtn");

    logoutBtn.addEventListener("click", async function () {
        logoutBtn.disabled = true;
        logoutBtn.textContent = "Logging out...";

        try {
            const response = await fetch("/api/logout", {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });

            const result = await response.json();

            if (result.success) {
                window.location.href = result.redirect_url || "/login";
            } else {
                logoutBtn.disabled = false;
                logoutBtn.textContent = "Log Out";
                alert("Logout failed. Please try again.");
            }
        } catch (error) {
            console.error("Logout error:", error);
            logoutBtn.disabled = false;
            logoutBtn.textContent = "Log Out";
        }
    });
});
