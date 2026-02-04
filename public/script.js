// File: public/script.js (Final Error-Handling Version)

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-upload');
    const fileNameSpan = document.getElementById('file-name');
    const resultText = document.getElementById('result-text');
    const themeToggle = document.getElementById('checkbox');
    const body = document.body;

    // --- Dark Mode Logic ---
    const applyTheme = (theme) => {
        body.dataset.theme = theme;
        themeToggle.checked = theme === 'dark';
        localStorage.setItem('theme', theme);
    };
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(savedTheme || (prefersDark ? 'dark' : 'light'));
    themeToggle.addEventListener('change', () => applyTheme(themeToggle.checked ? 'dark' : 'light'));

    // --- File Upload and AI Analysis Logic ---
    fileInput.addEventListener('change', async () => {
        const file = fileInput.files[0];
        if (!file) return;

        fileNameSpan.textContent = file.name;
        resultText.textContent = '';
        resultText.classList.add('loading');

        try {
            const response = await fetch('/api/narrate', {
                method: 'POST',
                headers: { 'Content-Type': file.type },
                body: file,
            });

            // If the server response is not OK (e.g., 500 error), get the error message from the body
            if (!response.ok) {
                // Try to parse the error message from the server's JSON response
                const errorData = await response.json().catch(() => {
                    // If the response isn't JSON, create a generic error
                    return { error: `Server returned a non-JSON error: ${response.status} ${response.statusText}` };
                });
                // Throw an error that will be caught by the catch block below
                throw new Error(errorData.error || `An unknown server error occurred.`);
            }

            const data = await response.json();
            resultText.classList.remove('loading');

            if (data.caption) {
                const caption = data.caption.charAt(0).toUpperCase() + data.caption.slice(1);
                resultText.textContent = caption;
            } else {
                throw new Error("Received a valid response, but no caption was found.");
            }

        } catch (error) {
            console.error("Error during analysis:", error); // This logs the full error to the browser console for debugging
            resultText.classList.remove('loading');
            
            // --- NEW, MORE ROBUST ERROR DISPLAY ---
            // Display the specific error message on the screen
            resultText.textContent = `Error: ${error.message}`;
        }
    });
});
