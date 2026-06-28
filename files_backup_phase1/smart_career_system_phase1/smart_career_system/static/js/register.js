/* =====================================================
   register.js
   Handles client-side validation and submission
   for the Registration page.
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("registerForm");
    const registerBtn = document.getElementById("registerBtn");

    const fullNameInput = document.getElementById("full_name");
    const emailInput = document.getElementById("email");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm_password");

    registerForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        hideAlert();

        const fullName = fullNameInput.value.trim();
        const email = emailInput.value.trim();
        const username = usernameInput.value.trim();
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        let isValid = true;

        // ----- Full Name -----
        if (fullName === "") {
            showFieldError("full_name", "Full name is required.");
            isValid = false;
        } else if (!isValidFullName(fullName)) {
            showFieldError("full_name", "Full name should contain only letters and spaces.");
            isValid = false;
        } else {
            clearFieldError("full_name");
        }

        // ----- Email -----
        if (email === "") {
            showFieldError("email", "Email is required.");
            isValid = false;
        } else if (!isValidEmail(email)) {
            showFieldError("email", "Please enter a valid email address.");
            isValid = false;
        } else {
            clearFieldError("email");
        }

        // ----- Username -----
        if (username === "") {
            showFieldError("username", "Username is required.");
            isValid = false;
        } else if (!isValidUsername(username)) {
            showFieldError("username", "Username must be 3-30 characters (letters, numbers, underscores).");
            isValid = false;
        } else {
            clearFieldError("username");
        }

        // ----- Password -----
        if (password === "") {
            showFieldError("password", "Password is required.");
            isValid = false;
        } else if (!isValidPassword(password)) {
            showFieldError("password", "Password must be at least 6 characters.");
            isValid = false;
        } else {
            clearFieldError("password");
        }

        // ----- Confirm Password -----
        if (confirmPassword === "") {
            showFieldError("confirm_password", "Please confirm your password.");
            isValid = false;
        } else if (password !== confirmPassword) {
            showFieldError("confirm_password", "Passwords do not match.");
            isValid = false;
        } else {
            clearFieldError("confirm_password");
        }

        if (!isValid) {
            return;
        }

        // ----- Submit to backend -----
        registerBtn.disabled = true;
        registerBtn.textContent = "Registering...";

        try {
            const response = await fetch("/api/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    full_name: fullName,
                    email: email,
                    username: username,
                    password: password,
                    confirm_password: confirmPassword
                })
            });

            const result = await response.json();

            if (result.success) {
                showAlert(result.message, "success");
                registerForm.reset();
                setTimeout(() => {
                    window.location.href = "/login";
                }, 1200);
            } else {
                showAlert(result.message || "Registration failed.", "error");
            }
        } catch (error) {
            console.error("Registration error:", error);
            showAlert("Something went wrong. Please try again.", "error");
        } finally {
            registerBtn.disabled = false;
            registerBtn.textContent = "Register";
        }
    });

    // Clear errors as user types
    [fullNameInput, emailInput, usernameInput, passwordInput, confirmPasswordInput].forEach((input) => {
        input.addEventListener("input", function () {
            clearFieldError(input.id);
        });
    });
});
