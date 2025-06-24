// List Previous Daily Puzzles JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        });
    }

    // Add loading states for buttons
    const solveButtons = document.querySelectorAll('.challenge-actions .btn');
    
    solveButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Loading...';
            this.disabled = true;
            
            // Re-enable after a short delay if the page doesn't navigate
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 3000);
        });
    });

    // Add smooth scroll to top when pagination is used
    const paginationLinks = document.querySelectorAll('.pagination .page-link');
    
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Smooth scroll to top after a short delay to allow page load
            setTimeout(() => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }, 100);
        });
    });

    // Add animation to challenge cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Initially hide cards and observe them
    const challengeCards = document.querySelectorAll('.challenge-card');
    challengeCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });

    // Add keyboard navigation for cards
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            const focusedElement = document.activeElement;
            if (focusedElement.classList.contains('challenge-card')) {
                const solveButton = focusedElement.querySelector('.btn-primary, .btn-outline-primary');
                if (solveButton) {
                    e.preventDefault();
                    solveButton.click();
                }
            }
        }
    });

    // Make cards focusable and add hover effects
    challengeCards.forEach(card => {
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', `Challenge for ${card.querySelector('.challenge-date').textContent.trim()}`);
        
        card.addEventListener('focus', function() {
            this.style.outline = '2px solid #9de0f6';
            this.style.outlineOffset = '2px';
        });
        
        card.addEventListener('blur', function() {
            this.style.outline = 'none';
        });
    });
});

// Function to show loading overlay (optional enhancement)
function showLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-spinner">
            <i class="bi bi-hourglass-split"></i>
            <p>Loading challenge...</p>
        </div>
    `;
    document.body.appendChild(overlay);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (overlay.parentNode) {
            overlay.remove();
        }
    }, 5000);
}

// Function to handle per-page changes smoothly
function handlePerPageChange() {
    const perPageSelect = document.getElementById('per_page');
    if (perPageSelect) {
        perPageSelect.addEventListener('change', function() {
            showLoadingOverlay();
        });
    }
}
