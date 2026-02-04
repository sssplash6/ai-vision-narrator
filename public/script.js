// File: public/script.js

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-upload');
    const fileNameSpan = document.getElementById('file-name');
    const resultText = document.getElementById('result-text');
    const themeToggle = document.getElementById('checkbox');
    const body = document.body;

    const applyTheme = (theme) => {
        body.dataset.theme = theme;
        themeToggle.checked = theme === 'dark';
        localStorage.setItem('theme', theme);
    };
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(savedTheme || (prefersDark ? 'dark' : 'light'));
    themeToggle.addEventListener('change', () => applyTheme(themeToggle.checked ? 'dark' : 'light'));

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        fileNameSpan.textContent = file.name;
        resultText.textContent = '';
        resultText.classList.add('loading');

        const reader = new FileReader();
        reader.readAsDataURL(file); // This reads the file as a base64 string

        reader.onload = async () => {
            const imageBase64 = reader.result;

            try {
                const response = await fetch('/api/narrate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: imageBase64 }), // Send as JSON
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ error: `Server error: ${response.status}` }));
                    throw new Error(errorData.error);
                }

                const data = await response.json();
                resultText.classList.remove('loading');

                if (data.caption) {
                    const caption = data.caption.charAt(0).toUpperCase() + data.caption.slice(1);
                    resultText.textContent = caption;
                } else {
                    throw new Error("Invalid response from server.");
                }

            } catch (error) {
                console.error("Error during analysis:", error);
                resultText.classList.remove('loading');
                resultText.textContent = `Error: ${error.message}`;
            }
        };
        
        reader.onerror = () => {
            resultText.classList.remove('loading');
            resultText.textContent = 'Error reading the file.';
        };
    });
});
