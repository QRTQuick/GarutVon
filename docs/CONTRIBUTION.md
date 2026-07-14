# GarutVON v2 — Contribution Guide

Thank you for your interest in contributing to **GarutVON v2**! To maintain production quality, please follow the guidelines below.

---

## 1. Code Quality Guidelines

- **PEP 8 Rules:** Python code must strictly adhere to standard formatting guidelines.
- **Strict JavaScript ES6 rules:** Avoid third-party UI libraries like jQuery, Tailwind, or Bootstrap. Utilize vanilla HTML5, CSS3 variables, and clean, modular ES6 classes.
- **No Mock Data:** Do not leave mock arrays in production components. Load records dynamically from REST endpoints.
- **No TODO comments:** Do not push incomplete workflows with `TODO` markers. Every feature must be production-ready.

---

## 2. Git and Commits Workflow

We follow a structured Git release process:
1. **Branch off Main:** Create descriptive feature branches:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make Modular Commits:** Commit often with clear messages:
   ```bash
   git commit -m "feat: implement Pillow PNG to ICO conversion rules"
   ```
3. **Run Unit Tests:** Ensure your additions do not break existing pipelines.
4. **Open a Draft Pull Request:** Open a Draft PR on GitHub to gather reviews and run automated CI checks before merging.
