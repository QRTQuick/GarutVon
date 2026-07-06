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
