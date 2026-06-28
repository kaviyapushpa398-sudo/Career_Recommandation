/* =====================================================
   validation.js
   Shared client-side validation helper functions
   for the Smart Career Recommendation System.
   ===================================================== */

/**
 * Validates an email address format.
 * @param {string} email
 * @returns {boolean}
 */
function isValidEmail(email) {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email.trim());
}

/**
 * Validates a username (letters, numbers, underscores, 3-30 chars).
 * @param {string} username
 * @returns {boolean}
 */
function isValidUsername(username) {
    const pattern = /^[a-zA-Z0-9_]{6,30}$/;
    return pattern.test(username.trim());
}

/**
 * Validates password length (min 6 characters).
 * @param {string} password
 * @returns {boolean}
 */
function isValidPassword(password) {
    return password.length >= 6;
}

/**
 * Validates that full name contains only letters and spaces, min 2 chars.
 * @param {string} name
 * @returns {boolean}
 */
function isValidFullName(name) {
    const pattern = /^[a-zA-Z\s]{2,100}$/;
    return pattern.test(name.trim());
}

/**
 * Displays an error message under a specific field
 * and highlights the input with an error border.
 * @param {string} inputId - The id of the input element
 * @param {string} message - The error message to display
 */
function showFieldError(inputId, message) {
    const input = document.getElementById(inputId);
    const errorSpan = document.getElementById(`error_${inputId}`);

    if (input) {
        input.classList.add("input-error");
        input.classList.remove("input-success");
    }
    if (errorSpan) {
        errorSpan.textContent = message;
    }
}

/**
 * Clears the error message and styling for a specific field.
 * @param {string} inputId - The id of the input element
 */
function clearFieldError(inputId) {
    const input = document.getElementById(inputId);
    const errorSpan = document.getElementById(`error_${inputId}`);

    if (input) {
        input.classList.remove("input-error");
        input.classList.add("input-success");
    }
    if (errorSpan) {
        errorSpan.textContent = "";
    }
}

/**
 * Shows a top-level alert box message (success or error).
 * @param {string} message
 * @param {"success"|"error"} type
 */
function showAlert(message, type = "error") {
    const alertBox = document.getElementById("alertBox");
    if (!alertBox) return;

    alertBox.textContent = message;
    alertBox.classList.remove("hidden", "success", "error");
    alertBox.classList.add(type);
}

/**
 * Hides the alert box.
 */
function hideAlert() {
    const alertBox = document.getElementById("alertBox");
    if (!alertBox) return;
    alertBox.classList.add("hidden");
}
