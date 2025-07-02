document.addEventListener('DOMContentLoaded', () => {
    const taskInput = document.getElementById('task-input');
    const runAgentBtn = document.getElementById('run-agent-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultContainer = document.getElementById('result-container');
    const resultOutput = document.getElementById('result-output');

    const apiUrl = 'https://kp-seo-auto-commenter.onrender.com/api/v1/agent/run';

    runAgentBtn.addEventListener('click', async () => {
        const task = taskInput.value.trim();
        if (!task) {
            alert('Please enter a topic.');
            return;
        }

        // Show loading state
        loadingIndicator.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        runAgentBtn.disabled = true;

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ task: task }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            
            // Assuming the structure is { status: 'success', result: { status: 'success', output: '...' } }
            if (data.result && data.result.output) {
                resultOutput.textContent = data.result.output;
            } else {
                throw new Error('Invalid response format from the server.');
            }

            resultContainer.classList.remove('hidden');

        } catch (error) {
            console.error('Error running agent:', error);
            resultOutput.textContent = `An error occurred: ${error.message}`;
            resultContainer.classList.remove('hidden');
        } finally {
            // Hide loading state
            loadingIndicator.classList.add('hidden');
            runAgentBtn.disabled = false;
        }
    });
});
