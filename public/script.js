// File: public/script.js (Final-final Error Handling Version)

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
            const reader = new FileReader();
            reader.readAsDataURL(file); // Read the file as a base64 string

            reader.onload = async () => {
                const imageBase64 = reader.result;

                const response = await fetch('/api/narrate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: imageBase64 }),
                });

                // If the server response is not OK (e.g., 500 error), get the raw text of the error
                if (!response.ok) {
                    const errorText = await response.text(); // Get the raw error text from the server
                    // Throw an error that contains this raw text. This is the most robust way.
                    throw new Error(`Server responded with status ${response.status}: ${errorText}`);
                }

                const data = await response.json();
                resultText.classList.remove('loading');

                if (data.caption) {
                    const caption = data.caption.charAt(0).toUpperCase() + data.caption.slice(1);
                    resultText.textContent = caption;
                } else {
                    throw new Error("Invalid successful response from server.");
                }
            };
            
            reader.onerror = () => {
                throw new Error('Failed to read the local file.');
            };

        } catch (error) {
            console.error("Error during analysis:", error); // Log the full error to the browser console for debugging
            resultText.classList.remove('loading');
            
            // Display the specific error message directly on the screen
            resultText.textContent = `Error: ${error.message}`;
        }
    });
});
