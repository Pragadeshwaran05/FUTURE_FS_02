// Apply the selected theme
function setTheme(theme) {

    // Save theme
    localStorage.setItem("theme", theme);

    // Remove existing theme classes
    document.body.classList.remove("light-theme", "dark-theme");

    // Apply new theme
    document.body.classList.add(theme + "-theme");

    // Update theme icon (if it exists)
    const toggle = document.getElementById("theme-toggle");

    if (toggle) {

        if (theme === "dark") {
            toggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
        } else {
            toggle.innerHTML = '<i class="bi bi-moon-fill"></i>';
        }

    }
}

// Load saved theme on every page
document.addEventListener("DOMContentLoaded", function () {

    const savedTheme = localStorage.getItem("theme") || "light";

    setTheme(savedTheme);

    // Home page theme button
    const toggle = document.getElementById("theme-toggle");

    if (toggle) {

        toggle.addEventListener("click", function () {

            const current = localStorage.getItem("theme") || "light";

            const next = current === "light" ? "dark" : "light";

            setTheme(next);

        });

    }

});
// Settings Page Buttons
const lightBtn = document.getElementById("light-theme-btn");
const darkBtn = document.getElementById("dark-theme-btn");

if (lightBtn) {
    lightBtn.addEventListener("click", function () {
        setTheme("light");
    });
}

if (darkBtn) {
    darkBtn.addEventListener("click", function () {
        setTheme("dark");
    });
}