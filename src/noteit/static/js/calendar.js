document.addEventListener('DOMContentLoaded', (event) => {
    flatpickr("#expiration_date", {
        inline: true,
        time_24hr: true,
        enableTime: true,
        enableSeconds: true,
        dateFormat: "d-m-Y, H:i:S",
        disable: [
            function(date) {
                var now = new Date();
                return (date < now);
            }
        ],
    });
})
