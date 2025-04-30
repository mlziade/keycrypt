document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (menuToggle) {
        menuToggle.addEventListener('click', function () {
            navLinks.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }

    // Close menu when clicking on a link (for mobile)
    const navLinksItems = document.querySelectorAll('.nav-links a, .nav-links button');
    navLinksItems.forEach(item => {
        item.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                navLinks.classList.remove('active');
                menuToggle.classList.remove('active');
            }
        });
    });
});