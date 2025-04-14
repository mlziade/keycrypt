document.addEventListener('DOMContentLoaded', function() {
    const reportButton = document.getElementById('reportButton');
    const reportForm = document.getElementById('reportForm');
    
    if (reportButton && reportForm) {
        reportButton.addEventListener('click', function() {
            if (confirm('Are you sure you want to report this puzzle?')) {
                reportForm.submit();
            }
        });
    }
});