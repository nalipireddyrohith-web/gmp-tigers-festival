const countdown = document.getElementById("countdown");

if (countdown) {

    // Change this date to your festival date
    const eventDate = new Date("September 17, 2026 08:00:00").getTime();

    function updateCountdown() {

        const now = new Date().getTime();
        const distance = eventDate - now;

        if (distance <= 0) {
            countdown.innerHTML = "🎉 Happy Vinayaka Chavithi!";
            return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        countdown.innerHTML =
            `${days} Days ${hours} Hours ${minutes} Minutes ${seconds} Seconds`;
    }

    updateCountdown();
    setInterval(updateCountdown, 1000);
}
