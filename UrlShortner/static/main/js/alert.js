document.addEventListener("DOMContentLoaded", function () {
    const alert = document.getElementById("flash-alert");
    const closeBtn = document.getElementById("alert-close");

    if (alert) {
        alert.style.transition = "all 0.3s ease-out";
        alert.style.transform = "translate(-50%, -20px)";
        alert.style.opacity = "10";

        // Trigger fade/slide-in
        setTimeout(() => {
            alert.style.transform = "translate(-50%, 0)";
            alert.style.opacity = "1";
        }, 50);

        setTimeout(() => {
            alert.style.transition = "all 0.3s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translate(-50%, -10px)";
            setTimeout(() => alert.remove(), 300); // remove after transition
        }, 3000);

        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                alert.style.transition = "all 0.3s ease";
                alert.style.opacity = "0";
                alert.style.transform = "translate(-50%, -10px)";
                setTimeout(() => alert.remove(), 300);
            });
        }
    }
});