document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll(".flash-alert");

    alerts.forEach((alert) => {
        alert.style.opacity = "0";
        alert.style.transform = "translateY(-10px)";
        setTimeout(() => {
            alert.style.transition = "all 0.3s ease-out";
            alert.style.opacity = "1";
            alert.style.transform = "translateY(0)";
        }, 50);

        setTimeout(() => {
            alert.style.transition = "all 0.3s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            setTimeout(() => alert.remove(), 300);
        }, 3000);

        const closeBtn = alert.querySelector(".alert-close");
        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                alert.style.transition = "all 0.3s ease";
                alert.style.opacity = "0";
                alert.style.transform = "translateY(-10px)";
                setTimeout(() => alert.remove(), 300);
            });
        }
    });

    const timerDisplay = document.getElementById("timerDisplay");
    const mybutton = document.getElementById("mybuttonId");
    let countDownDate = new Date().getTime() + (1 * 30 * 1000);

    let x = setInterval(() => {
        let now = new Date().getTime();
        let distance = countDownDate - now;
        let seconds = Math.floor((distance % (1000 * 60)) / 1000);

        if (distance > 0) {
            timerDisplay.innerHTML = `You can resend the email in <span class="font-semibold">${seconds}</span> seconds.`;
        } else {
            clearInterval(x);
            timerDisplay.innerHTML = "You can now resend the email.";
            mybutton.disabled = false;
            mybutton.classList.remove("cursor-not-allowed", "bg-blue-600");
            mybutton.classList.add("cursor-pointer", "bg-blue-700", "hover:bg-blue-800", "transition");
        }
    }, 1000);
});