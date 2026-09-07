document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://127.0.0.1:8000';
    
    const questionInput = document.getElementById('questionInput');
    const askBtn = document.getElementById('askBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const responseArea = document.getElementById('responseArea');
    const errorArea = document.getElementById('errorArea');
    const errorText = document.getElementById('errorText');
    const statusIndicator = document.getElementById('statusIndicator');
    const answerText = document.getElementById('answerText');
    const sourcesBox = document.getElementById('sourcesBox');
    const sourcesList = document.getElementById('sourcesList');

    askBtn.addEventListener('click', handleAsk);

    // Allow pressing Enter (without Shift) to submit
    questionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleAsk();
        }
    });

    async function handleAsk() {
        const question = questionInput.value.trim();
        
        if (!question) {
            showError("Please enter a question.");
            return;
        }

        // Reset UI
        hideError();
        responseArea.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');
        askBtn.disabled = true;

        try {
            const response = await fetch(`${API_BASE_URL}/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question })
            });

            const data = await response.json();

            if (!response.ok) {
                // Handle validation or other API errors
                let errMsg = "An error occurred.";
                if (data.detail && Array.isArray(data.detail)) {
                    errMsg = data.detail.map(d => d.msg).join(", ");
                } else if (data.detail) {
                    errMsg = data.detail;
                }
                throw new Error(errMsg);
            }

            renderResponse(data);

        } catch (error) {
            console.error("Error calling API:", error);
            showError(error.message || "Failed to communicate with the server.");
        } finally {
            loadingIndicator.classList.add('hidden');
            askBtn.disabled = false;
        }
    }

    function renderResponse(data) {
        // Status
        statusIndicator.textContent = data.status;
        statusIndicator.className = 'status-indicator'; // reset
        
        if (data.status === 'ANSWERED') {
            statusIndicator.classList.add('status-answered');
        } else if (data.status === 'CONFLICT') {
            statusIndicator.classList.add('status-conflict');
        } else if (data.status === 'NOT_COVERED') {
            statusIndicator.classList.add('status-not-covered');
        } else {
            // Error or unknown
            statusIndicator.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
            statusIndicator.style.color = '#ef4444';
        }

        // Answer
        answerText.textContent = data.answer || "No answer provided.";

        // Sources
        sourcesList.innerHTML = '';
        if (data.sources && data.sources.length > 0) {
            sourcesBox.classList.remove('hidden');
            
            data.sources.forEach((source, index) => {
                const card = document.createElement('div');
                card.className = 'source-card';
                
                const meta = source.metadata || {};
                
                // Header (Filename & Score)
                const header = document.createElement('div');
                header.className = 'source-header';
                
                const filename = document.createElement('span');
                filename.className = 'source-filename';
                filename.textContent = `Source: ${source.source || meta.source || "Unknown"}`;
                
                const score = document.createElement('span');
                score.className = 'source-score';
                const sim_score = source.similarity_score !== undefined ? source.similarity_score : (meta.similarity_score !== undefined ? meta.similarity_score : source.score);
                if (sim_score !== undefined) {
                    score.textContent = `Similarity Score: ${Number(sim_score).toFixed(4)}`;
                }
                
                header.appendChild(filename);
                header.appendChild(score);
                
                // Meta details (Section, Page, Row)
                const metaDiv = document.createElement('div');
                metaDiv.className = 'source-meta';
                
                // Use derived fields from the API if present, else fallback to raw metadata
                const section_val = source.section || meta.section;
                const page_val = source.page || meta.page;
                const row_val = source.row || meta.row;
                
                const metaParts = [];
                if (section_val) metaParts.push(`Section: ${section_val}`);
                if (page_val) metaParts.push(`Page: ${page_val}`);
                if (row_val !== undefined && row_val !== null) metaParts.push(`Row: ${row_val}`);
                
                if (metaParts.length > 0) {
                    metaDiv.innerHTML = metaParts.join('<br>');
                }
                
                // Content
                const content = document.createElement('div');
                content.className = 'source-content';
                content.textContent = source.content || "Content unavailable.";
                
                card.appendChild(header);
                if (metaParts.length > 0) card.appendChild(metaDiv);
                card.appendChild(content);
                
                sourcesList.appendChild(card);
            });
        } else {
            sourcesBox.classList.add('hidden');
        }

        responseArea.classList.remove('hidden');
    }

    function showError(message) {
        errorText.textContent = message;
        errorArea.classList.remove('hidden');
    }

    function hideError() {
        errorArea.classList.add('hidden');
    }
});
