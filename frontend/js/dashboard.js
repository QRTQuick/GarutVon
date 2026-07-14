/* GarutVON v2 - User Dashboard, Conversion Portal, and Donations Interface */

document.addEventListener("DOMContentLoaded", () => {
    initDashboard();
});

// CSRF Utility Helper
function getCSRFToken() {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; gv_csrf=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return "";
}

async function initDashboard() {
    const isDashboard = document.getElementById("dashboard-section");
    if (!isDashboard) return;
    
    // Load general user profile metrics
    await loadUserProfile();
    await loadConversionHistory();
    await loadAPIKeys();
    await loadDonationStats();
    
    // Attach handlers
    setupConverterWidget();
    setupProfileSettings();
    setupAPIKeyManager();
    setupDonationPage();
}

// 1. Retrieve & Render User Profile Details
async function loadUserProfile() {
    try {
        const response = await fetch("/api/auth/me");
        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }
        
        const result = await response.json();
        if (response.ok && result.status === "success") {
            const user = result.data;
            
            // Populating visual dashboard fields
            const nameElements = document.querySelectorAll(".user-name-placeholder");
            nameElements.forEach(el => el.textContent = user.full_name);
            
            const emailElements = document.querySelectorAll(".user-email-placeholder");
            emailElements.forEach(el => el.textContent = user.email);
            
            // Render quota metrics
            const quotaUsage = document.getElementById("quota-conversions-count");
            if (quotaUsage) quotaUsage.textContent = `${user.conversions_this_week} / ${user.conversion_limit_weekly}`;
            
            const planText = document.getElementById("user-current-plan");
            if (planText) planText.textContent = user.plan_name;
            
            // Fill setting inputs
            const fullNameInput = document.getElementById("settings_full_name");
            if (fullNameInput) fullNameInput.value = user.full_name;
            
            const promoPref = document.getElementById("pref_promo");
            if (promoPref) promoPref.checked = user.email_promo_pref;
            
            const securityPref = document.getElementById("pref_security");
            if (securityPref) securityPref.checked = user.email_security_pref;
        }
    } catch (err) {
        console.error("Failed to read user me metrics:", err);
    }
}

// 2. Fetch & Render Conversion logs
async function loadConversionHistory() {
    const tableBody = document.getElementById("history-table-body");
    if (!tableBody) return;
    
    try {
        const response = await fetch("/api/convert/history");
        const result = await response.json();
        
        if (response.ok && result.status === "success") {
            const history = result.history;
            if (history.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="5" class="text-center" style="color: var(--text-muted)">No conversion records found. Begin converting your first file!</td></tr>`;
                return;
            }
            
            tableBody.innerHTML = history.map(h => {
                const sizeKb = (h.input_size / 1024).toFixed(1);
                return `
                    <tr>
                        <td><strong>${h.input_name}</strong></td>
                        <td>${sizeKb} KB</td>
                        <td><span class="badge-coming" style="background: rgba(255,255,255,0.05); color: #fff;">${h.input_format} &rarr; ${h.output_format}</span></td>
                        <td><span class="status-badge ${h.status.toLowerCase()}">${h.status}</span></td>
                        <td>
                            ${h.download_url ? `<a href="${h.download_url}" class="btn btn-sm btn-primary">Download</a>` : `<span style="color: var(--text-muted)">N/A</span>`}
                        </td>
                    </tr>
                `;
            }).join("");
        }
    } catch (err) {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center" style="color: var(--error)">Failed to retrieve logs.</td></tr>`;
    }
}

// 3. Complete Image conversion pipeline upload integration
function setupConverterWidget() {
    const uploadForm = document.getElementById("image-converter-form");
    if (!uploadForm) return;
    
    const dragArea = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-upload-input");
    
    if (dragArea && fileInput) {
        dragArea.addEventListener("click", () => fileInput.click());
        
        dragArea.addEventListener("dragover", (e) => {
            e.preventDefault();
            dragArea.classList.add("dragover");
        });
        
        dragArea.addEventListener("dragleave", () => {
            dragArea.classList.remove("dragover");
        });
        
        dragArea.addEventListener("drop", (e) => {
            e.preventDefault();
            dragArea.classList.remove("dragover");
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                updateDragAreaLabel(e.dataTransfer.files[0].name);
            }
        });
        
        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) {
                updateDragAreaLabel(fileInput.files[0].name);
            }
        });
    }
    
    function updateDragAreaLabel(name) {
        const label = document.getElementById("upload-label");
        if (label) label.innerHTML = `Selected File: <strong style="color: var(--text-primary)">${name}</strong>`;
    }
    
    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const submitBtn = uploadForm.querySelector("button[type='submit']");
        const originalText = submitBtn.innerHTML;
        
        const files = fileInput.files;
        const targetFormat = document.getElementById("target-format-select").value;
        
        if (files.length === 0) {
            window.showNotification("Upload Error", "Choose a valid image file to proceed.", "warning");
            return;
        }
        
        const formData = new FormData();
        formData.append("file", files[0]);
        formData.append("format", targetFormat);
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner" style="width: 14px; height: 14px; border-width: 1px; margin: 0 8px 0 0; display: inline-block;"></span>Converting Image...`;
        
        try {
            const response = await fetch("/api/convert/image", {
                method: "POST",
                body: formData
            });
            const result = await response.json();
            
            if (response.ok && result.status === "success") {
                window.showNotification("Conversion Complete", result.message, "success");
                // Immediately refresh quota dashboard and histories
                await loadUserProfile();
                await loadConversionHistory();
                
                // Offer direct download trigger
                if (result.download_url) {
                    window.location.href = result.download_url;
                }
            } else if (response.status === 429) {
                window.showNotification("Quota Blocked", result.message, "warning");
            } else {
                window.showNotification("Conversion Error", result.message || "Failed to process image.", "error");
            }
        } catch (err) {
            window.showNotification("Pipeline Failed", "Server side processing network failure.", "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

// 4. Developer API keys panel manager
async function loadAPIKeys() {
    const keysTable = document.getElementById("api-keys-table-body");
    if (!keysTable) return;
    
    try {
        const response = await fetch("/api/developer/keys");
        const result = await response.json();
        
        if (response.ok && result.status === "success") {
            const keys = result.keys;
            if (keys.length === 0) {
                keysTable.innerHTML = `<tr><td colspan="4" class="text-center" style="color: var(--text-muted)">No active API Keys. Generate a secure key to build cloud utilities.</td></tr>`;
                return;
            }
            
            keysTable.innerHTML = keys.map(k => `
                <tr>
                    <td><strong>${k.name}</strong></td>
                    <td><code>${k.key_prefix}*****</code></td>
                    <td>${k.created_at}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="revokeKey(${k.id})">Revoke</button>
                    </td>
                </tr>
            `).join("");
        }
    } catch (err) {
        keysTable.innerHTML = `<tr><td colspan="4" class="text-center" style="color: var(--error)">Failed to retrieve developer key list.</td></tr>`;
    }
}

function setupAPIKeyManager() {
    const createKeyForm = document.getElementById("create-api-key-form");
    if (!createKeyForm) return;
    
    createKeyForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const submitBtn = createKeyForm.querySelector("button[type='submit']");
        const originalText = submitBtn.textContent;
        
        const name = document.getElementById("api_key_name").value.trim();
        if (!name) return;
        
        submitBtn.disabled = true;
        submitBtn.textContent = "Creating Sec Key...";
        
        try {
            const response = await fetch("/api/developer/keys", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "X-CSRF-Token": getCSRFToken()
                },
                body: JSON.stringify({ name })
            });
            const result = await response.json();
            
            if (response.ok && result.status === "success") {
                window.showNotification("Key Created", result.message, "success");
                
                // Show raw key modal / alert for copier convenience
                const keyHolder = document.getElementById("raw-generated-key-container");
                if (keyHolder) {
                    keyHolder.classList.remove("hidden");
                    document.getElementById("raw-api-key-display").value = result.api_key;
                }
                
                createKeyForm.reset();
                await loadAPIKeys();
            } else {
                window.showNotification("Error", result.message || "Failed to create key.", "error");
            }
        } catch (err) {
            window.showNotification("Network Error", "Unable to contact API Portal.", "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
    
    // Copy key display handler
    const copyBtn = document.getElementById("copy-raw-key-btn");
    if (copyBtn) {
        copyBtn.addEventListener("click", () => {
            const keyInput = document.getElementById("raw-api-key-display");
            keyInput.select();
            document.execCommand("copy");
            window.showNotification("Copied", "Raw API key copied securely to clipboard.", "success");
        });
    }
}

// Global revoke API key function mapped to components
window.revokeKey = async (keyId) => {
    if (!confirm("Are you sure you want to revoke this API key? This will permanently sever any connected cloud automation flows!")) return;
    
    try {
        const response = await fetch(`/api/developer/keys/${keyId}`, {
            method: "DELETE",
            headers: {
                "X-CSRF-Token": getCSRFToken()
            }
        });
        const result = await response.json();
        
        if (response.ok && result.status === "success") {
            window.showNotification("Key Revoked", result.message, "success");
            await loadAPIKeys();
        } else {
            window.showNotification("Error", result.message || "Failed to revoke key.", "error");
        }
    } catch (err) {
        window.showNotification("Network Offline", "Failed to revoke key.", "error");
    }
};

// 5. Account Security Settings & Preferences updating
function setupProfileSettings() {
    const updateForm = document.getElementById("profile-settings-form");
    if (updateForm) {
        updateForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = updateForm.querySelector("button[type='submit']");
            const originalText = submitBtn.textContent;
            
            const full_name = document.getElementById("settings_full_name").value.trim();
            const email_promo_pref = document.getElementById("pref_promo").checked;
            const email_security_pref = document.getElementById("pref_security").checked;
            
            submitBtn.disabled = true;
            submitBtn.textContent = "Saving preferences...";
            
            try {
                const response = await fetch("/api/auth/update-profile", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRF-Token": getCSRFToken()
                    },
                    body: JSON.stringify({
                        action: "update_info",
                        full_name,
                        email_promo_pref,
                        email_security_pref
                    })
                });
                const result = await response.json();
                
                if (response.ok && result.status === "success") {
                    window.showNotification("Settings Saved", result.message, "success");
                    await loadUserProfile();
                } else {
                    window.showNotification("Security Error", result.message, "error");
                }
            } catch (err) {
                window.showNotification("Offline", "Settings sync failed.", "error");
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
    
    // Change password form integration
    const changePassForm = document.getElementById("change-password-form");
    if (changePassForm) {
        changePassForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const submitBtn = changePassForm.querySelector("button[type='submit']");
            const originalText = submitBtn.textContent;
            
            const current_password = document.getElementById("current_password").value;
            const new_password = document.getElementById("new_password").value;
            const confirm_new = document.getElementById("confirm_new_password").value;
            
            if (new_password !== confirm_new) {
                window.showNotification("Input Validation", "New passwords do not match.", "warning");
                return;
            }
            
            submitBtn.disabled = true;
            submitBtn.textContent = "Updating security...";
            
            try {
                const response = await fetch("/api/auth/update-profile", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRF-Token": getCSRFToken()
                    },
                    body: JSON.stringify({
                        action: "change_password",
                        current_password,
                        new_password
                    })
                });
                const result = await response.json();
                
                if (response.ok && result.status === "success") {
                    window.showNotification("Password Updated", result.message, "success");
                    changePassForm.reset();
                } else {
                    window.showNotification("Security Refused", result.message, "error");
                }
            } catch (err) {
                window.showNotification("Error", "Server password rotation offline.", "error");
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // Permanent delete account trigger
    const deleteAccountForm = document.getElementById("delete-account-form");
    if (deleteAccountForm) {
        deleteAccountForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const emailConfirm = document.getElementById("delete_confirm_email").value.trim().lowerCase;
            
            if (!confirm("Are you absolutely sure you want to permanently delete your GarutVON account? This action is irreversible and purges all credentials, API Keys, subscriptions and conversion histories!")) {
                return;
            }
            
            try {
                const response = await fetch("/api/auth/update-profile", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRF-Token": getCSRFToken()
                    },
                    body: JSON.stringify({
                        action: "delete_account",
                        confirm_email: document.getElementById("delete_confirm_email").value.trim()
                    })
                });
                const result = await response.json();
                
                if (response.ok && result.status === "success") {
                    alert(result.message);
                    window.location.href = "/";
                } else {
                    window.showNotification("Action Refused", result.message, "error");
                }
            } catch (err) {
                window.showNotification("Network Error", "Purge request failed.", "error");
            }
        });
    }
}

// 6. Community Donations & Happer payment processing page setup
async function loadDonationStats() {
    const bar = document.getElementById("donation-progress-bar");
    const progressLabel = document.getElementById("donation-progress-label");
    const donorContainer = document.getElementById("recent-donors-container");
    
    if (!bar && !donorContainer) return;
    
    try {
        const response = await fetch("/api/donations/stats");
        const result = await response.json();
        
        if (response.ok && result.status === "success") {
            // Render Progress Bar
            if (bar) bar.style.width = `${result.percent_complete}%`;
            if (progressLabel) progressLabel.textContent = `$${result.current_progress.toFixed(2)} raised of $${result.target_amount.toFixed(2)} monthly hosting target (${result.percent_complete}%)`;
            
            // Render Recent Donors
            if (donorContainer) {
                if (result.recent_donors.length === 0) {
                    donorContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">No recent donations. Be the first to fuel GarutVON!</p>`;
                    return;
                }
                
                donorContainer.innerHTML = result.recent_donors.map(d => `
                    <div style="background-color: var(--bg-tertiary); border: 1px solid var(--border-color); padding: 12px; border-radius: var(--radius-sm); margin-bottom: 12px;">
                        <div class="flex justify-between align-center" style="margin-bottom: 6px;">
                            <strong style="font-size: 13px; color: var(--text-primary)">${d.name}</strong>
                            <span style="font-family: var(--font-mono); font-size: 12px; color: var(--success); font-weight: bold;">+${d.currency} ${d.amount.toFixed(2)}</span>
                        </div>
                        ${d.message ? `<p style="font-size: 12px; color: var(--text-secondary); italic">${d.message}</p>` : ""}
                    </div>
                `).join("");
            }
        }
    } catch (err) {
        console.error("Donation stats fetch failure:", err);
    }
}

function setupDonationPage() {
    const donateForm = document.getElementById("donation-initiation-form");
    if (!donateForm) return;
    
    donateForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const submitBtn = donateForm.querySelector("button[type='submit']");
        const originalText = submitBtn.textContent;
        
        const amount = document.getElementById("donation_amount").value;
        const donor_name = document.getElementById("donor_name").value.trim();
        const donor_message = document.getElementById("donor_message").value.trim();
        
        submitBtn.disabled = true;
        submitBtn.textContent = "Initializing Happer Widget...";
        
        try {
            const response = await fetch("/api/donations/initiate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ amount, currency: "USD", donor_name, donor_message })
            });
            const result = await response.json();
            
            if (response.ok && result.success) {
                window.showNotification("Payment Interface Open", "Complete your secure transaction via Happer inside the embed widget.", "success");
                
                // Show Happer Secure Embed Element Container
                const embedSection = document.getElementById("happer-embed-container");
                if (embedSection) {
                    embedSection.classList.remove("hidden");
                    // Smoothly scroll down to make it immediately visual
                    embedSection.scrollIntoView({ behavior: "smooth" });
                }
            } else {
                window.showNotification("Initialization Failed", result.message || "Failed to start Happer.", "error");
            }
        } catch (err) {
            window.showNotification("Offline", "Payment servers are temporarily offline.", "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}
