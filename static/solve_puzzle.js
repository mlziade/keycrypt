document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded");

    // Check for CSRF token
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfTokenElement) {
        console.error("CSRF token not found in the form");
        return;
    }
    const csrfToken = csrfTokenElement.value;

    // Check for test buttons
    const testButtons = document.querySelectorAll('.test-answer-btn');
    console.log(`Found ${testButtons.length} test buttons`);

    if (testButtons.length === 0) {
        console.error("No test buttons found with class 'test-answer-btn'");
        return;
    }

    testButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent any default behavior
            console.log("Test button clicked");

            const puzzleId = this.dataset.puzzleId;
            const questionId = this.dataset.questionId;
            console.log(`Checking answer for puzzle ${puzzleId}, question ${questionId}`);

            const answerInput = document.getElementById(`answer-${questionId}`);
            const feedbackDiv = document.getElementById(`feedback-${questionId}`);

            if (!answerInput) {
                console.error(`Input field with ID 'answer-${questionId}' not found`);
                return;
            }

            if (!feedbackDiv) {
                console.error(`Feedback div with ID 'feedback-${questionId}' not found`);
                return;
            }

            if (!answerInput.value.trim()) {
                feedbackDiv.textContent = "Please enter an answer";
                feedbackDiv.className = "feedback-message mt-2 text-warning";
                return;
            }

            // Disable button and show loading state
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Testing...';

            const apiUrl = `/puzzle/test_question/${puzzleId}/${questionId}/`;
            console.log(`Sending request to: ${apiUrl}`);

            fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `answer=${encodeURIComponent(answerInput.value)}`
            })
                .then(response => {
                    console.log("Received response:", response.status);
                    return response.json();
                })
                .then(data => {
                    console.log("Response data:", data);
                    // Enable button again
                    this.disabled = false;
                    this.innerHTML = '<i class="bi bi-check-circle"></i> Test';

                    if (data.status === 'success') {
                        // Correct answer
                        this.classList.remove('btn-outline-secondary', 'btn-danger');
                        this.classList.add('btn-success');
                        feedbackDiv.textContent = "Correct answer!";
                        feedbackDiv.className = "feedback-message mt-2 text-success";
                    } else {
                        // Wrong answer
                        this.classList.remove('btn-outline-secondary', 'btn-success');
                        this.classList.add('btn-danger');
                        feedbackDiv.textContent = "Incorrect answer. Try again.";
                        feedbackDiv.className = "feedback-message mt-2 text-danger";
                    }
                })
                .catch(error => {
                    console.error("Error processing request:", error);
                    this.disabled = false;
                    this.innerHTML = '<i class="bi bi-check-circle"></i> Test';
                    feedbackDiv.textContent = "Error testing answer. Please try again.";
                    feedbackDiv.className = "feedback-message mt-2 text-danger";
                });
        });
    });
});