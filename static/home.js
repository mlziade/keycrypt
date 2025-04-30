document.addEventListener('DOMContentLoaded', function() {
    const text = "KeyCrypt";
    const element = document.getElementById('keycrypt-text');
    const cursor = document.querySelector('.typing-cursor');
    const hackerChars = "!@#$%^&*()_+-=[]{}|;:,./<>?1234567890";
    let index = 0;
    
    // Reduced initial delay before typing starts (from 500ms to 300ms)
    setTimeout(startTyping, 300);
    
    function startTyping() {
        if (index < text.length) {
            // Create a new span for this character
            const charSpan = document.createElement('span');
            charSpan.classList.add('hacker-char');
            element.appendChild(charSpan);
            
            // Scramble effect (reduced scrambles from 5 to 3)
            let scrambleCount = 0;
            const maxScrambles = 4;
            
            // Reduced scramble interval from 50ms to 30ms
            const scrambleInterval = setInterval(() => {
                if (scrambleCount < maxScrambles) {
                    charSpan.textContent = hackerChars.charAt(Math.floor(Math.random() * hackerChars.length));
                    scrambleCount++;
                } else {
                    clearInterval(scrambleInterval);
                    charSpan.textContent = text.charAt(index);
                    charSpan.classList.add('revealed');
                    index++;
                    // Reduced delay between characters from 120ms to 80ms
                    setTimeout(startTyping, 100);
                }
            }, 30);
        } else {
            // Animation complete
            cursor.classList.add('blink');
        }
    }
});