document.addEventListener('DOMContentLoaded', function() {
    // Animate main card on load
    const mainCard = document.getElementById('mainCard');
    const footer = document.getElementById('footer');
    const links = document.querySelectorAll('[data-link]');
    
    setTimeout(() => {
        mainCard.classList.remove('opacity-0', 'translate-y-8');
    }, 100);
    
    setTimeout(() => {
        footer.classList.remove('opacity-0', 'translate-y-4');
    }, 600);
    
    // Animate links with stagger
    links.forEach((link, index) => {
        setTimeout(() => {
            link.classList.remove('opacity-0', 'translate-y-4');
        }, 800 + (index * 100));
    });

    // Back to top functionality
    const backToTopBtn = document.getElementById('backToTop');
    
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopBtn.classList.remove('opacity-0', 'pointer-events-none');
            } else {
                backToTopBtn.classList.add('opacity-0', 'pointer-events-none');
            }
        });

        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        // Add click effects to links
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                // Add a subtle scale effect
                this.style.transform = 'scale(0.95) translateY(-4px)';
                setTimeout(() => {
                this.style.transform = '';
                }, 150);
            });
        });

        // Parallax effect for background
        window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const backgrounds = document.querySelectorAll('.fixed .absolute');
    
        backgrounds.forEach((bg, index) => {
            const speed = (index + 1) * 0.1;
            bg.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
});