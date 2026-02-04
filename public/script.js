// File: public/script.js

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
    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (!file) return;

        fileNameSpan.textContent = file.name;
        resultText.textContent = ''; // Clear previous results
        resultText.classList.add('loading'); // Show "Analyzing..." text

        const reader = new FileReader();
        reader.readAsDataURL(file);

        reader.onload = async () => {
            const imageBase64 = reader.result;

            try {
                const response = await fetch('/api/narrate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: imageBase64 }),
                });

                if (!response.ok) {
                    throw new Error(`Server error: ${response.statusText}`);
                }

                const data = await response.json();
                resultText.classList.remove('loading');

                if (data.labels && data.labels.length > 0) {
                    // Format the labels into a natural sentence for dictation
                    const formattedText = `This image appears to contain: ${data.labels.join(', ')}.`;
                    resultText.textContent = formattedText;
                } else {
                    resultText.textContent = "I'm sorry, I couldn't identify any objects in this image.";
                }

            } catch (error) {
                console.error("Error:", error);
                resultText.classList.remove('loading');
                resultText.textContent = "An error occurred during analysis. Please try again.";
            }
        };

        reader.onerror = () => {
            resultText.classList.remove('loading');
            resultText.textContent = 'There was an error reading the file.';
        };
    });
});
