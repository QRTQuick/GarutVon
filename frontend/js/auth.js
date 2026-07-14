/* GarutVON v2 - User Authentication Handlers */

document.addEventListener("DOMContentLoaded", () => {
    initAuthForms();
});

function analyzePasswordStrength(password) {
    const value = password || "";
    let score = 0;
    const feedback = [];

    if (value.length >= 8) score += 1;
    if (value.length >= 12) score += 1;
    if (/[a-z]/.test(value)) score += 1;
    if (/[A-Z]/.test(value)) score += 1;
    if (/[0-9]/.test(value)) score += 1;
    if (/[^A-Za-z0-9]/.test(value)) score += 1;

    const lower = value.toLowerCase();
    const weakPatterns = ["123456", "password", "qwerty", "admin", "letmein", "welcome", "garutvon"];
    if (weakPatterns.some((pattern) => lower.includes(pattern))) {
        score = Math.max(0, score - 2);
        feedback.push("Avoid common words or predictable sequences.");
    }

    if (value.length < 8) {
        feedback.push("Use at least 8 characters.");
    }
    if (!/[A-Z]/.test(value)) {
        feedback.push("Add uppercase letters.");
    }
    if (!/[0-9]/.test(value)) {
        feedback.push("Add numbers.");
    }
    if (!/[^A-Za-z0-9]/.test(value)) {
        feedback.push("Add symbols for extra strength.");
    }

    const percent = Math.min(100, Math.max(0, Math.round((score / 6) * 100)));
    let label = "Very weak";
    let color = "var(--error)";

    if (score <= 1) {
        label = "Very weak";
        color = "var(--error)";
    } else if (score === 2) {
        label = "Weak";
        color = "var(--warning)";
    } else if (score === 3) {
        label = "Fair";
        color = "#facc15";
    } else if (score === 4) {
        label = "Good";
        color = "#22c55e";
    } else if (score >= 5) {
        label = "Strong";
        color = "var(--success)";
    }

    return { score, percent, label, color, feedback };
}

function bindPasswordStrengthMeter(passwordInputId, statusId, barId) {
    const passwordInput = document.getElementById(passwordInputId);
    const statusText = document.getElementById(statusId);
    const strengthBar = document.getElementById(barId);
    if (!passwordInput || !statusText || !strengthBar) return;

    const refresh = () => {
        const analysis = analyzePasswordStrength(passwordInput.value);
        statusText.textContent = analysis.label;
        statusText.style.color = analysis.color;
        strengthBar.style.width = `${analysis.percent}%`;
        strengthBar.style.background = analysis.color;
    };

    passwordInput.addEventListener("input", refresh);
    refresh();
    return refresh;
}

function initAuthForms() {
    // 1. REGISTER FORM SUBMISSION
    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        bindPasswordStrengthMeter("password", "password-strength-status", "password-strength-bar");
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = registerForm.querySelector("button[type='submit']");
            const originalText = submitBtn.textContent;
            
            const full_name = document.getElementById("full_name").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            const terms_agree = document.getElementById("terms_agree").checked;

            const strength = analyzePasswordStrength(password);
            if (strength.score < 3) {
                window.showNotification("Password Strength Warning", "Your password is weak. Use longer length, mixed-case letters, numbers and symbols.", "warning");
            }
            
            if (!terms_agree) {
                window.showNotification("Terms & Conditions", "You must agree to the Terms of Service to sign up.", "warning");
                return;
            }
            
            submitBtn.disabled = true;
            submitBtn.textContent = "Creating Account...";
            
            try {
                const response = await fetch("/api/auth/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ full_name, email, password })
                });
                
                const result = await response.json();
                if (response.ok) {
                    window.showNotification("Registration Successful", "We have dispatched a verification link to your email address.", "success");
                    registerForm.reset();
                    setTimeout(() => { window.location.href = "/login"; }, 3000);
                } else {
                    window.showNotification("Registration Failed", result.message || "Unknown validation error.", "error");
                }
            } catch (err) {
                window.showNotification("Network Error", "Unable to connect to registration API server.", "error");
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // 2. LOGIN FORM SUBMISSION
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = loginForm.querySelector("button[type='submit']");
            const originalText = submitBtn.textContent;
            
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            const remember_me = document.getElementById("remember_me")?.checked || false;
            
            submitBtn.disabled = true;
            submitBtn.textContent = "Authenticating...";
            
            try {
                const response = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password, remember_me })
                });
                
                const result = await response.json();
                if (response.ok) {
                    window.showNotification("Welcome Back", result.message, "success");
                    setTimeout(() => {
                        if (result.role === "admin") {
                            window.location.href = "/admin";
                        } else {
                            window.location.href = "/dashboard";
                        }
                    }, 1000);
                } else {
                    window.showNotification("Access Denied", result.message || "Invalid credentials.", "error");
                }
            } catch (err) {
                window.showNotification("Connection Failure", "Unable to communicate with credentials portal.", "error");
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // 3. FORGOT PASSWORD SUBMISSION
    const forgotForm = document.getElementById("forgot-password-form");
    if (forgotForm) {
        forgotForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = forgotForm.querySelector("button[type='submit']");
            const originalText = submitBtn.textContent;
            
            const email = document.getElementById("email").value.trim();
            submitBtn.disabled = true;
            submitBtn.textContent = "Sending Instructions...";
            
            try {
                const response = await fetch("/api/auth/forgot-password", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email })
                });
                const result = await response.json();
                window.showNotification("Reset Instructions Dispatched", result.message, "success");
                forgotForm.reset();
            } catch (err) {
                window.showNotification("Service Offline", "Server error dispatching reset credentials.", "error");
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // 4. RESET PASSWORD SUBMISSION
    const resetForm = document.getElementById("reset-password-form");
    if (resetForm) {
        bindPasswordStrengthMeter("password", "reset-password-strength-status", "reset-password-strength-bar");
        resetForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = resetForm.querySelector("button[type='submit']");
            const originalText = submitBtn.textContent;
            
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get("token");
            const password = document.getElementById("password").value;
            const confirm_password = document.getElementById("confirm_password").value;
            
            if (!token) {
                window.showNotification("Verification Error", "Reset token context is missing in your URL.", "error");
                return;
            }
            if (password !== confirm_password) {
                window.showNotification("Input Validation", "Passwords do not match.", "warning");
                return;
            }

            const strength = analyzePasswordStrength(password);
            if (strength.score < 3) {
                window.showNotification("Password Strength Warning", "Your new password is weak. Add complexity before saving.", "warning");
            }
            
            submitBtn.disabled = true;
            submitBtn.textContent = "Saving New Password...";
            
            try {
                const response = await fetch("/api/auth/reset-password", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ token, password })
                });
                const result = await response.json();
                if (response.ok) {
                    window.showNotification("Security Updated", "Your password has been changed. Redirecting to login...", "success");
                    setTimeout(() => { window.location.href = "/login"; }, 3000);
                } else {
                    window.showNotification("Link Expired", result.message || "Failed to reset password.", "error");
                }
            } catch (err) {
                window.showNotification("Network Offline", "Connection issue. Please retry.", "error");
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
}

// 5. EMAIL VERIFICATION TRIGGER (Automatic load for verify-email.html)
async function triggerEmailVerification() {
    const statusText = document.getElementById("verification-status");
    if (!statusText) return;
    
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("token");
    
    if (!token) {
        statusText.textContent = "Error: Invalid verification context. Missing token in parameter.";
        statusText.style.color = "var(--error)";
        return;
    }
    
    try {
        const response = await fetch("/api/auth/verify-email", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token })
        });
        const result = await response.json();
        
        if (response.ok) {
            statusText.textContent = "Account successfully verified! Redirecting you to login dashboard...";
            statusText.style.color = "var(--success)";
            setTimeout(() => { window.location.href = "/login"; }, 3000);
        } else {
            statusText.textContent = `Verification failed: ${result.message}`;
            statusText.style.color = "var(--error)";
        }
    } catch (err) {
        statusText.textContent = "Server connection lost. Unable to complete account registration checks.";
    }
}
window.triggerEmailVerification = triggerEmailVerification;
