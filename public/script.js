// File: public/script.js (Final Version for Hugging Face)

document.addEventListener('DOMContentLoaded', () => {
    // --- UI Elements ---
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
        resultText.textContent = ''; // Clear previous results
        resultText.classList.add('loading'); // Show "Analyzing..." text

        try {
            // This new version sends the raw image file directly. It's more efficient
            // and required by the Hugging Face Inference API.
            const response = await fetch('/api/narrate', {
                method: 'POST',
                headers: { 'Content-Type': file.type }, // Send the actual image mime type
                body: file, // The raw file object is the body
            });

            if (!response.ok) {
                // If the server returns an error (like 500), this will throw an error
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            resultText.classList.remove('loading');

            if (data.caption) {
                // The AI now returns a full sentence caption.
                // We'll make the first letter uppercase for a nicer presentation.
                const caption = data.caption.charAt(0).toUpperCase() + data.caption.slice(1);
                resultText.textContent = caption;
            } else if (data.error) {
                // Display specific errors from the backend if available
                resultText.textContent = `Error: ${data.error}`;
            } else {
                resultText.textContent = "I'm sorry, I couldn't generate a description for this image.";
            }

        } catch (error) {
            console.error("Error during fetch:", error);
            resultText.classList.remove('loading');
            resultText.textContent = "A client-side error occurred. Please check the console.";
        }
    });
});
