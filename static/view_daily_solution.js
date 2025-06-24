// View Daily Solution JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        });
    }

    // Add copy to clipboard functionality for solutions
    const solutionValues = document.querySelectorAll('.answer-value');
    
    solutionValues.forEach(answerElement => {
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'btn btn-sm btn-outline-secondary copy-btn';
        copyButton.innerHTML = '<i class="bi bi-clipboard"></i>';
        copyButton.title = 'Copy to clipboard';
        copyButton.type = 'button';
        
        // Style the copy button
        copyButton.style.position = 'absolute';
        copyButton.style.right = '0.5rem';
        copyButton.style.top = '0.5rem';
        copyButton.style.fontSize = '0.75rem';
        copyButton.style.padding = '0.25rem 0.5rem';
        
        // Make parent relative for positioning
        answerElement.style.position = 'relative';
        
        // Add copy functionality
        copyButton.addEventListener('click', function() {
            const textToCopy = answerElement.textContent.trim();
            
            navigator.clipboard.writeText(textToCopy).then(() => {
                // Show success feedback
                const originalIcon = this.innerHTML;
                this.innerHTML = '<i class="bi bi-check"></i>';
                this.classList.remove('btn-outline-secondary');
                this.classList.add('btn-success');
                
                setTimeout(() => {
                    this.innerHTML = originalIcon;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-outline-secondary');
                }, 2000);
            }).catch(err => {
                console.error('Could not copy text: ', err);
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = textToCopy;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    // Show success feedback
                    const originalIcon = this.innerHTML;
                    this.innerHTML = '<i class="bi bi-check"></i>';
                    this.classList.remove('btn-outline-secondary');
                    this.classList.add('btn-success');
                    
                    setTimeout(() => {
                        this.innerHTML = originalIcon;
                        this.classList.remove('btn-success');
                        this.classList.add('btn-outline-secondary');
                    }, 2000);
                } catch (err) {
                    console.error('Fallback copy failed: ', err);
                }
                document.body.removeChild(textArea);
            });
        });
        
        answerElement.appendChild(copyButton);
    });

    // Add copy functionality for the decrypted message
    const decryptedMessage = document.querySelector('.decrypted-message');
    if (decryptedMessage) {
        const copyMessageButton = document.createElement('button');
        copyMessageButton.className = 'btn btn-outline-primary btn-sm copy-message-btn';
        copyMessageButton.innerHTML = '<i class="bi bi-clipboard me-2"></i>Copy Message';
        copyMessageButton.type = 'button';
        copyMessageButton.style.marginTop = '1rem';
        
        copyMessageButton.addEventListener('click', function() {
            const messageText = decryptedMessage.textContent.trim();
            
            navigator.clipboard.writeText(messageText).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="bi bi-check me-2"></i>Copied!';
                this.classList.remove('btn-outline-primary');
                this.classList.add('btn-success');
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-outline-primary');
                }, 2000);
            }).catch(err => {
                console.error('Could not copy message: ', err);
            });
        });
        
        decryptedMessage.parentNode.appendChild(copyMessageButton);
    }

    // Add smooth reveal animation for solution items
    const solutionItems = document.querySelectorAll('.solution-item');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -30px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Initially hide items and observe them
    solutionItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        item.style.transition = `opacity 0.6s ease ${index * 0.2}s, transform 0.6s ease ${index * 0.2}s`;
        observer.observe(item);
    });

    // Add keyboard navigation for better accessibility
    document.addEventListener('keydown', function(e) {
        // ESC key to close/go back
        if (e.key === 'Escape') {
            const backButton = document.querySelector('.header-actions .btn-outline-secondary');
            if (backButton) {
                backButton.click();
            }
        }
    });

    // Add loading states for navigation buttons
    const navigationButtons = document.querySelectorAll('.header-actions .btn, .solution-navigation .btn');
    
    navigationButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!this.href || this.href === '#') return;
            
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Loading...';
            this.disabled = true;
            
            // Re-enable after a short delay if the page doesn't navigate
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 3000);        });
    });
});

// Function to handle smooth animations and interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add any additional functionality for the solution page here
});
