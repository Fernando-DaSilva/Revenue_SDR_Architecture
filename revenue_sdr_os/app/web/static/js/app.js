/*
 * Revenue SDR OS — app.js
 * Microinteratividade que nao depende de framework.
 */

document.documentElement.classList.add("js");

// Auto-dismiss de alerts efemeros (ex: erro de login) apos 6s.
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-auto-dismiss]").forEach((el) => {
        setTimeout(() => {
            el.style.transition = "opacity 0.4s ease";
            el.style.opacity = "0";
            setTimeout(() => el.remove(), 400);
        }, 6000);
    });
});
