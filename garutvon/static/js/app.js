const navToggle = document.querySelector(".nav-toggle");
const nav = document.querySelector(".nav");
if (navToggle && nav) {
  navToggle.addEventListener("click", () => nav.classList.toggle("open"));
}

document.querySelectorAll('a[href^="/download/track"]').forEach((link) => {
  link.addEventListener("click", () => {
    window.localStorage.setItem("garutvon:lastDownloadClick", new Date().toISOString());
  });
});

document.querySelectorAll("[data-toggle-password]").forEach((button) => {
  button.addEventListener("click", () => {
    const input = button.closest(".password-row")?.querySelector("input");
    if (!input) return;
    const visible = input.type === "text";
    input.type = visible ? "password" : "text";
    button.innerHTML = visible ? '<i class="fa-solid fa-eye"></i>' : '<i class="fa-solid fa-eye-slash"></i>';
    button.setAttribute("aria-label", visible ? "Show password" : "Hide password");
  });
});

const registerForm = document.querySelector("[data-register-form]");
if (registerForm) {
  const passwordInput = registerForm.querySelector("[data-password-input]");
  const confirmInput = registerForm.querySelector("[data-confirm-password]");
  const meterBar = registerForm.querySelector("[data-meter-bar]");
  const message = registerForm.querySelector("[data-password-message]");
  const commonPasswords = new Set(["password", "password123", "12345678", "123456789", "qwerty123", "garutvon", "admin123", "letmein123"]);

  const updatePasswordState = () => {
    const password = passwordInput.value;
    const checks = {
      length: password.length >= 10,
      upper: /[A-Z]/.test(password),
      lower: /[a-z]/.test(password),
      number: /\d/.test(password),
      symbol: /[^A-Za-z0-9]/.test(password),
      common: password.length > 0 && !commonPasswords.has(password.toLowerCase())
    };
    const passed = Object.values(checks).filter(Boolean).length;

    Object.entries(checks).forEach(([rule, ok]) => {
      const item = registerForm.querySelector(`[data-rule="${rule}"]`);
      if (item) item.classList.toggle("ok", ok);
    });

    if (meterBar) {
      meterBar.style.width = `${(passed / 6) * 100}%`;
      meterBar.dataset.level = passed < 3 ? "weak" : passed < 5 ? "medium" : "strong";
    }

    const mismatch = confirmInput.value && password !== confirmInput.value;
    if (message) {
      if (!password) message.innerHTML = '<i class="fa-solid fa-circle-info"></i> Password strength will appear as you type.';
      else if (mismatch) message.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Passwords do not match.';
      else if (passed < 5) message.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Your password is too weak.';
      else message.innerHTML = '<i class="fa-solid fa-circle-check"></i> Strong password.';
      message.classList.toggle("ok", passed >= 5 && !mismatch);
    }
  };

  passwordInput.addEventListener("input", updatePasswordState);
  confirmInput.addEventListener("input", updatePasswordState);
  registerForm.addEventListener("submit", (event) => {
    updatePasswordState();
    const weak = registerForm.querySelectorAll(".password-rules li.ok").length < 5;
    if (weak || passwordInput.value !== confirmInput.value) {
      event.preventDefault();
      passwordInput.focus();
    }
  });
}
