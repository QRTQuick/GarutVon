/* GarutVON v2 - Shared Layout Components & Toast Notifications */

document.addEventListener("DOMContentLoaded", () => {
    initStickyHeader();
    initMobileNav();
    initCookieConsentBanner();
    initFooterSocialLink();
    initWireRope();
    dismissLoadingScreen();
});

// 1. Sticky Navigation Scroll tracker
function initStickyHeader() {
    const header = document.querySelector("header.sticky-nav");
    if (!header) return;
    
    window.addEventListener("scroll", () => {
        if (window.scrollY > 30) {
            header.classList.add("scrolled");
        } else {
            header.classList.remove("scrolled");
        }
    });
}

// 2. Mobile Responsive Nav Menu Toggle
function initMobileNav() {
    const hamburger = document.querySelector(".hamburger");
    const menu = document.querySelector(".nav-menu");
    if (!hamburger || !menu) return;
    
    hamburger.addEventListener("click", () => {
        menu.classList.toggle("active");
        hamburger.classList.toggle("open");
    });
    
    // Close when active links are selected
    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", () => {
            menu.classList.remove("active");
            hamburger.classList.remove("open");
        });
    });
}

// 3. Smooth Loading Screen Fade-out
function dismissLoadingScreen() {
    const loader = document.querySelector(".loading-screen");
    if (!loader) return;
    
    setTimeout(() => {
        loader.style.opacity = "0";
        setTimeout(() => {
            loader.style.display = "none";
        }, 300);
    }, 400); // Small duration to ensure nice micro-animation
}

function getCookieValue(name) {
    const cookieString = document.cookie.split(";").map((item) => item.trim());
    const cookieItem = cookieString.find((item) => item.startsWith(`${name}=`));
    return cookieItem ? decodeURIComponent(cookieItem.split("=")[1]) : null;
}

function setCookie(name, value, days) {
    const expires = new Date(Date.now() + (days * 24 * 60 * 60 * 1000)).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}

function initCookieConsentBanner() {
    if (getCookieValue("garutvon_cookie_consent") === "accepted") return;
    if (document.querySelector(".cookie-banner")) return;

    const banner = document.createElement("div");
    banner.className = "cookie-banner";
    banner.innerHTML = `
        <div class="cookie-banner-body">
            <strong>Cookie Notice</strong>
            <p>We use cookies for secure sessions, cleaner UI performance, and WPA-friendly compliance. Accept cookies to keep the site fast and secure.</p>
            <div class="cookie-banner-actions">
                <a href="/cookies" class="footer-link">Cookie Settings</a>
                <a href="/terms" class="footer-link">Terms &amp; Conditions</a>
            </div>
        </div>
        <button class="btn btn-primary cookie-accept-btn">Accept Cookies</button>
    `;

    document.body.appendChild(banner);
    banner.querySelector(".cookie-accept-btn").addEventListener("click", () => {
        setCookie("garutvon_cookie_consent", "accepted", 365);
        banner.style.opacity = "0";
        setTimeout(() => banner.remove(), 300);
        window.showNotification("Cookie Preference Saved", "You accepted cookies for a faster, smoother experience.", "success");
    });
}

function initFooterSocialLink() {
    document.querySelectorAll(".footer-bottom").forEach((footer) => {
        if (footer.querySelector(".footer-social")) return;
        const social = document.createElement("div");
        social.className = "footer-social";
        social.innerHTML = `
            <a href="https://twitter.com/GarutVon" target="_blank" rel="noopener noreferrer">@GarutVon</a>
        `;
        footer.appendChild(social);

        // add mailto contact next to social
        if (!footer.querySelector('.footer-email')) {
            const mail = document.createElement('div');
            mail.className = 'footer-email';
            mail.style.marginLeft = '16px';
            mail.innerHTML = `<a href="mailto:garutvon@gmail.com" class="footer-link">garutvon@gmail.com</a>`;
            footer.appendChild(mail);
        }

        // append built-by credit
        if (!footer.querySelector('.footer-credit')) {
            const credit = document.createElement('div');
            credit.className = 'footer-credit';
            credit.textContent = 'Built by QuickRedTech';
            footer.appendChild(credit);
        }
    });
}

function initWireRope() {
    // append a decorative animated wire-rope to the footer-bottom
    const bottom = document.querySelector('.footer-bottom');
    if (!bottom) return;
    if (bottom.querySelector('.wire-rope')) return;

    const rope = document.createElement('div');
    rope.className = 'wire-rope';
    rope.setAttribute('aria-hidden', 'true');

    // create repeated rope strands for visual depth
    for (let i = 0; i < 3; i++) {
        const strand = document.createElement('div');
        strand.className = 'wire-strand';
        strand.style.setProperty('--i', i);
        rope.appendChild(strand);
    }

    bottom.appendChild(rope);
}

// dynamically inject a favicon link to use the provided assets path
if (typeof window !== 'undefined') {
    const head = document.head || document.getElementsByTagName('head')[0];
    if (head && !document.querySelector("link[rel='icon'][href='/assets/garutvon-favicon.png']")) {
        const link = document.createElement('link');
        link.rel = 'icon';
        link.href = '/assets/garutvon-favicon.png';
        link.type = 'image/png';
        head.appendChild(link);
    }
}

// 4. Premium Toast Notification Center Helper
class NotificationCenter {
    static init() {
        let container = document.querySelector(".toast-container");
        if (!container) {
            container = document.createElement("div");
            container.className = "toast-container";
            document.body.appendChild(container);
        }
        return container;
    }

    static show(title, description, type = "success") {
        const container = this.init();
        
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-desc">${description}</div>
            </div>
            <div class="toast-close">&times;</div>
        `;
        
        container.appendChild(toast);
        
        // Auto dismiss after 5 seconds
        const timer = setTimeout(() => {
            toast.style.animation = "fadeOut 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards";
            setTimeout(() => { toast.remove(); }, 300);
        }, 5000);
        
        // Manual Dismiss
        toast.querySelector(".toast-close").addEventListener("click", () => {
            clearTimeout(timer);
            toast.style.animation = "fadeOut 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards";
            setTimeout(() => { toast.remove(); }, 300);
        });
    }
}

// Export to globally accessible context
window.showNotification = (title, desc, type) => {
    NotificationCenter.show(title, desc, type);
};
