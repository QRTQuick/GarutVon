/* GarutVON v2 - Admin Panel Dashboard, Logs, Feature Flags, and Donations Audit */

document.addEventListener("DOMContentLoaded", () => {
    initAdmin();
});

async function initAdmin() {
    const isAdminSec = document.getElementById("admin-section");
    if (!isAdminSec) return;
    
    // Authenticate and load metrics
    await loadAdminMetrics();
    await loadAdminUsers();
    await loadAdminLogs();
    await loadAdminFlags();
    await loadAdminDonations();
    
    setupAdminSearch();
}

// 1. Fetch & Render general platform statistics
async function loadAdminMetrics() {
    try {
        const response = await fetch("/api/admin/metrics");
        if (response.status === 403 || response.status === 401) {
            alert("Admin session expired. Please log in with admin privileges.");
            window.location.href = "/login";
            return;
        }
        
        const result = await response.json();
        if (response.ok && result.status === "success") {
            const m = result.metrics;
            document.getElementById("stat_total_users").textContent = m.total_users;
            document.getElementById("stat_conversions").textContent = m.total_conversions;
            document.getElementById("stat_api_keys").textContent = m.active_api_keys;
            document.getElementById("stat_donations_all").textContent = `$${m.total_donated.toFixed(2)}`;
            document.getElementById("stat_donations_monthly").textContent = `$${m.monthly_donated.toFixed(2)}`;
        }
    } catch (err) {
        console.error("Failed to load admin metrics:", err);
    }
}

// 2. Fetch & Render User list inside panel
async function loadAdminUsers() {
    const container = document.getElementById("admin-users-table-body");
    if (!container) return;
    
    try {
        const response = await fetch("/api/admin/users");
        const result = await response.json();
        
        if (response.ok && result.status === "success") {
            const users = result.users;
            container.innerHTML = users.map(u => `
                <tr data-user-email="${u.email}">
                    <td><strong>${u.full_name}</strong></td>
                    <td><code>${u.email}</code></td>
                    <td>${u.created_at}</td>
                    <td>
                        <span class="status-badge ${u.is_verified ? "completed" : "pending"}">${u.is_verified ? "Verified" : "Unverified"}</span>
                    </td>
                    <td>
                        <span class="status-badge ${u.is_active ? "completed" : "failed"}">${u.is_active ? "Active" : "Banned"}</span>
                    </td>
                    <td>
                        <button class="btn btn-sm ${u.is_active ? "btn-danger" : "btn-primary"}" onclick="toggleUserStatus(${u.id}, ${u.is_active})">
                            ${u.is_active ? "Ban" : "Activate"}
                        </button>
                    </td>
                </tr>
            `).join("");
        }
    } catch (err) {
        container.innerHTML = `<tr><td colspan="6" class="text-center" style="color: var(--error)">Failed to load accounts.</td></tr>`;
    }
}

window.toggleUserStatus = async (userId, currentStatus) => {
    const action = currentStatus ? "ban" : "activate";
    if (!confirm(`Are you sure you want to ${action} this user?`)) return;
    
    try {
        const response = await fetch(`/api/admin/users/${userId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ is_active: !currentStatus })
        });
        const result = await response.json();
        
        if (response.ok && result.status === "success") {
            window.showNotification("Account Updated", result.message, "success");
            await loadAdminUsers();
        } else {
            window.showNotification("Error", result.message, "error");
        }
    } catch (err) {
        window.showNotification("Offline", "Action failed.", "error");
    }
};

// 3. Fetch & Render audit trails
async function loadAdminLogs() {
    const logBox = document.getElementById("admin-logs-table-body");
    if (!logBox) return;
    
    try {
        const response = await fetch("/api/admin/logs");
        const result = await response.json();
        
        if (response.ok && result.status === "success") {
            logBox.innerHTML = result.logs.map(l => `
                <tr data-log-action="${l.action}">
                    <td><code style="color: var(--text-secondary)">${l.created_at}</code></td>
                    <td><strong style="font-size: 12px; font-family: var(--font-mono)">${l.action}</strong></td>
                    <td><code>${l.ip_address}</code></td>
                    <td><span style="font-size: 13px; color: var(--text-secondary)">${l.details || ""}</span></td>
                </tr>
            `).join("");
        }
    } catch (err) {
        logBox.innerHTML = `<tr><td colspan="4" class="text-center" style="color: var(--error)">Failed to retrieve logs.</td></tr>`;
    }
}

// 4. Fetch & Render modular feature flags toggle switches
async function loadAdminFlags() {
    const container = document.getElementById("admin-flags-container");
    if (!container) return;
    
    try {
        const response = await fetch("/api/admin/flags");
        const result = await response.json();
        
        if (response.ok && result.status === "success") {
            container.innerHTML = result.flags.map(f => `
                <div style="background-color: var(--bg-tertiary); border: 1px solid var(--border-color); padding: 16px; border-radius: var(--radius-sm); margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 14px; color: var(--text-primary)">${f.name.replace(/_/g, ' ').toUpperCase()}</strong>
                        <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">${f.description}</p>
                    </div>
                    <label class="switch">
                        <input type="checkbox" ${f.is_enabled ? "checked" : ""} onchange="toggleFeatureFlag(${f.id}, this.checked)">
                        <span class="slider"></span>
                    </label>
                </div>
            `).join("");
        }
    } catch (err) {
        container.innerHTML = `<p style="color: var(--error)">Failed to read flags.</p>`;
    }
}

window.toggleFeatureFlag = async (flagId, isEnabled) => {
    try {
        const response = await fetch("/api/admin/flags", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: flagId, is_enabled: isEnabled })
        });
        const result = await response.json();
        
        if (response.ok && result.status === "success") {
            window.showNotification("Feature Updated", result.message, "success");
            await loadAdminFlags();
        } else {
            window.showNotification("Error", result.message, "error");
        }
    } catch (err) {
        window.showNotification("Offline", "Action failed.", "error");
    }
};

// 5. Donations Audit Ledger
async function loadAdminDonations() {
    const container = document.getElementById("admin-donations-table-body");
    if (!container) return;
    
    try {
        const response = await fetch("/api/admin/donations");
        const result = await response.json();
        
        if (response.ok && result.status === "success") {
            const donations = result.donations;
            if (donations.length === 0) {
                container.innerHTML = `<tr><td colspan="7" class="text-center" style="color: var(--text-muted)">No donations recorded in ledger.</td></tr>`;
                return;
            }
            
            container.innerHTML = donations.map(d => `
                <tr data-donation-donor="${d.donor_name}">
                    <td><strong>${d.donor_name}</strong></td>
                    <td><strong style="color: var(--success)">$${d.amount.toFixed(2)}</strong></td>
                    <td><code>${d.payment_provider}</code></td>
                    <td><code>${d.transaction_ref}</code></td>
                    <td><span class="status-badge ${d.payment_status.toLowerCase()}">${d.payment_status}</span></td>
                    <td>${d.created_at}</td>
                    <td style="font-size: 12px; color: var(--text-secondary)">${d.donor_message || "—"}</td>
                </tr>
            `).join("");
        }
    } catch (err) {
        container.innerHTML = `<tr><td colspan="7" class="text-center" style="color: var(--error)">Failed to retrieve donations ledger.</td></tr>`;
    }
}

// 6. Admin Panel list filters & CSV download trigger
function setupAdminSearch() {
    const userSearch = document.getElementById("admin-user-search-input");
    if (userSearch) {
        userSearch.addEventListener("input", (e) => {
            const filter = e.target.value.toLowerCase();
            document.querySelectorAll("#admin-users-table-body tr").forEach(row => {
                const email = row.getAttribute("data-user-email") || "";
                if (email.toLowerCase().includes(filter)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        });
    }
    
    const exportBtn = document.getElementById("admin-export-donations-csv");
    if (exportBtn) {
        exportBtn.addEventListener("click", () => {
            window.location.href = "/api/admin/donations?export=csv";
        });
    }
}
