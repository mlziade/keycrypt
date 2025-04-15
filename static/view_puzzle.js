document.addEventListener('DOMContentLoaded', function() {
    // Report button functionality
    const reportButton = document.getElementById('reportButton');
    const reportForm = document.getElementById('reportForm');
    
    if (reportButton && reportForm) {
        reportButton.addEventListener('click', function() {
            if (confirm('Are you sure you want to report this puzzle?')) {
                reportForm.submit();
            }
        });
    }
    
    // Copy URL button functionality
    const copyUrlButton = document.getElementById('copyUrlButton');
    
    if (copyUrlButton) {
        copyUrlButton.addEventListener('click', function() {
            navigator.clipboard.writeText(window.location.href.replace("view", "solve"))
                .then(() => {
                    // Show feedback that URL was copied
                    const originalText = copyUrlButton.innerHTML;
                    copyUrlButton.innerHTML = '<i class="bi bi-check"></i> Copied!';
                    
                    setTimeout(() => {
                        copyUrlButton.innerHTML = originalText;
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy URL: ', err);
                    alert('Failed to copy URL to clipboard');
                });
        });
    }
});