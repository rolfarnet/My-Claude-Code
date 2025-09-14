// Global variables
let currentQuestions = [];
let currentAnswers = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadCategories();
    loadStatistics();
});

// Tab switching functionality
function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab and activate button
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

// Setup event listeners
function setupEventListeners() {
    // Excel file upload
    const excelFile = document.getElementById('excel-file');
    const excelUploadArea = document.getElementById('excel-upload-area');
    
    excelFile.addEventListener('change', handleExcelUpload);
    
    // Drag and drop for Excel files
    excelUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        excelUploadArea.classList.add('dragover');
    });
    
    excelUploadArea.addEventListener('dragleave', () => {
        excelUploadArea.classList.remove('dragover');
    });
    
    excelUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        excelUploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0 && (files[0].name.endsWith('.xlsx') || files[0].name.endsWith('.xls'))) {
            excelFile.files = files;
            handleExcelUpload({ target: { files: files } });
        }
    });
    
    // Historical files upload
    const historicalFiles = document.getElementById('historical-files');
    const historicalUploadArea = document.getElementById('historical-upload-area');
    
    historicalFiles.addEventListener('change', handleHistoricalUpload);
    
    // Drag and drop for historical files
    historicalUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        historicalUploadArea.classList.add('dragover');
    });
    
    historicalUploadArea.addEventListener('dragleave', () => {
        historicalUploadArea.classList.remove('dragover');
    });
    
    historicalUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        historicalUploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            historicalFiles.files = files;
            handleHistoricalUpload({ target: { files: files } });
        }
    });
}

// Handle Excel file upload
async function handleExcelUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/upload-client-questions', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        currentQuestions = result.questions;
        
        displayQuestions(result.questions, result.file_name);
        
    } catch (error) {
        showAlert('Fehler beim Hochladen der Excel-Datei: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display extracted questions
function displayQuestions(questions, fileName) {
    const questionsPreview = document.getElementById('questions-preview');
    const questionsList = document.getElementById('questions-list');
    
    questionsList.innerHTML = `
        <div class="alert success">
            <strong>Erfolg!</strong> ${questions.length} Fragen aus ${fileName} extrahiert
        </div>
    `;
    
    questions.forEach((question, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question-item';
        questionDiv.innerHTML = `
            <h4>Frage ${index + 1}</h4>
            <p>${question}</p>
        `;
        questionsList.appendChild(questionDiv);
    });
    
    questionsPreview.style.display = 'block';
}

// Generate answers for all questions
async function generateAllAnswers() {
    if (currentQuestions.length === 0) {
        showAlert('Keine Fragen zum Verarbeiten vorhanden', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/generate-answers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentQuestions)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const answers = await response.json();
        currentAnswers = answers;
        
        displayAnswers(answers);
        
    } catch (error) {
        showAlert('Fehler beim Generieren der Antworten: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display generated answers
function displayAnswers(answers) {
    const answersSection = document.getElementById('answers-section');
    const answersContainer = document.getElementById('answers-container');
    
    answersContainer.innerHTML = '';
    
    answers.forEach((answer, index) => {
        const answerDiv = document.createElement('div');
        answerDiv.className = 'answer-item';
        
        const confidenceClass = getConfidenceClass(answer.confidence_score);
        
        answerDiv.innerHTML = `
            <div class="question">F${index + 1}: ${currentQuestions[index]}</div>
            <div class="answer">${answer.answer}</div>
            <div class="confidence ${confidenceClass}">
                Vector distance metric: ${(answer.confidence_score * 100).toFixed(1)}%
            </div>
            <div class="confidence ${getFuzzyClass(answer.fuzzy_score)}">
                Text pattern match: ${(answer.fuzzy_score * 100).toFixed(1)}%
            </div>
            ${answer.sources.length > 0 ? `
                <div class="sources">
                    <h5>Quellen (${answer.sources.length})</h5>
                    ${answer.sources.slice(0, 3).map(source => `
                        <div class="source-item">
                            <strong>F:</strong> ${source.question_text.substring(0, 100)}...
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        `;
        
        answersContainer.appendChild(answerDiv);
    });
    
    answersSection.style.display = 'block';
}

// Handle historical data upload
async function handleHistoricalUpload(event) {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;
    
    showLoading();
    
    try {
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });
        
        const response = await fetch('/upload-historical-data', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        displayProcessingResults(result.results);
        loadStatistics(); // Refresh statistics
        
    } catch (error) {
        showAlert('Fehler beim Hochladen historischer Daten: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display processing results
function displayProcessingResults(results) {
    const processingResults = document.getElementById('processing-results');
    const resultsContainer = document.getElementById('results-container');
    
    resultsContainer.innerHTML = '';
    
    let totalPairs = 0;
    
    results.forEach(result => {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'alert ' + (result.status === 'success' ? 'success' : 'error');
        
        if (result.status === 'success') {
            totalPairs += result.qa_pairs_extracted;
            resultDiv.innerHTML = `
                <strong>${result.file_name}</strong><br>
                ✅ ${result.qa_pairs_extracted} Q&A-Paare erfolgreich extrahiert
                (${result.processing_time.toFixed(2)}s)
            `;
        } else {
            resultDiv.innerHTML = `
                <strong>${result.file_name}</strong><br>
                ❌ ${result.status}
            `;
        }
        
        resultsContainer.appendChild(resultDiv);
    });
    
    if (totalPairs > 0) {
        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'alert success';
        summaryDiv.innerHTML = `
            <strong>Zusammenfassung:</strong> ${totalPairs} neue Q&A-Paare zur Wissensbasis hinzugefügt
        `;
        resultsContainer.insertBefore(summaryDiv, resultsContainer.firstChild);
    }
    
    processingResults.style.display = 'block';
}

// Generate answer for single question
async function generateSingleAnswer() {
    const question = document.getElementById('single-question-input').value.trim();
    const context = document.getElementById('context-input').value.trim();
    const category = document.getElementById('category-filter').value;
    
    if (!question) {
        showAlert('Bitte geben Sie eine Frage ein', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        let endpoint = '/generate-answer';
        let body;
        
        if (category) {
            endpoint = '/generate-answer-by-category';
            const formData = new FormData();
            formData.append('question', question);
            formData.append('category', category);
            if (context) formData.append('context', context);
            body = formData;
        } else {
            body = JSON.stringify({ question, context: context || null });
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: category ? {} : { 'Content-Type': 'application/json' },
            body: body
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const answer = await response.json();
        displaySingleAnswer(answer);
        
    } catch (error) {
        showAlert('Fehler beim Generieren der Antwort: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Display single answer
function displaySingleAnswer(answer) {
    const resultDiv = document.getElementById('single-answer-result');
    const contentDiv = document.getElementById('single-answer-content');
    const sourcesDiv = document.getElementById('single-answer-sources');
    
    const confidenceClass = getConfidenceClass(answer.confidence_score);
    
    contentDiv.innerHTML = `
        <div class="answer">${answer.answer}</div>
        <div class="confidence ${confidenceClass}">
            Vector distance metric: ${(answer.confidence_score * 100).toFixed(1)}%
        </div>
        <div class="confidence ${getFuzzyClass(answer.fuzzy_score)}">
            Text pattern match: ${(answer.fuzzy_score * 100).toFixed(1)}%
        </div>
    `;
    
    if (answer.sources && answer.sources.length > 0) {
        sourcesDiv.innerHTML = `
            <div class="sources">
                <h5>Quellen (${answer.sources.length})</h5>
                ${answer.sources.map(source => `
                    <div class="source-item">
                        <strong>F:</strong> ${source.question_text}<br>
                        <strong>Kategorie:</strong> ${source.category}
                        ${source.client ? `<br><strong>Kunde:</strong> ${source.client}` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        sourcesDiv.innerHTML = '';
    }
    
    resultDiv.style.display = 'block';
}

// Load categories
async function loadCategories() {
    try {
        const response = await fetch('/categories');
        const result = await response.json();
        
        const categoryFilter = document.getElementById('category-filter');
        categoryFilter.innerHTML = '<option value="">All Categories</option>';
        
        result.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category.charAt(0).toUpperCase() + category.slice(1);
            categoryFilter.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch('/stats');
        const stats = await response.json();
        
        document.getElementById('total-qa-pairs').textContent = stats.total_qa_pairs;
        document.getElementById('category-count').textContent = stats.category_count;
        
        // Display categories
        const categoriesList = document.getElementById('categories-list');
        categoriesList.innerHTML = '';
        
        if (stats.categories.length > 0) {
            stats.categories.forEach(category => {
                const categorySpan = document.createElement('span');
                categorySpan.className = 'category-tag';
                categorySpan.textContent = category.charAt(0).toUpperCase() + category.slice(1);
                categoriesList.appendChild(categorySpan);
            });
        } else {
            categoriesList.innerHTML = '<p>Keine Kategorien verfügbar. Laden Sie zuerst historische Daten hoch.</p>';
        }
        
    } catch (error) {
        console.error('Error loading statistics:', error);
        document.getElementById('total-qa-pairs').textContent = 'Fehler';
        document.getElementById('category-count').textContent = 'Fehler';
    }
}

// Download template
async function downloadTemplate() {
    try {
        const response = await fetch('/download-template');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'client_questions_template.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showAlert('Vorlage erfolgreich heruntergeladen', 'success');
        
    } catch (error) {
        showAlert('Fehler beim Herunterladen der Vorlage: ' + error.message, 'error');
    }
}

// Export answers
function exportAnswers() {
    if (currentAnswers.length === 0) {
        showAlert('Keine Antworten zum Exportieren vorhanden', 'warning');
        return;
    }
    
    // Create workbook and worksheet
    const wb = XLSX.utils.book_new();
    
    // Prepare data for Excel with proper column headers (German)
    const excelData = [
        ['Frage', 'Kommentar zur Antwort', 'Antwort', 'Vector Distance Metric (%)', 'Text Pattern Match (%)', 'Quellen']
    ];
    
    currentAnswers.forEach((answer, index) => {
        const { comment, answer: cleanAnswer } = separateCommentAndAnswer(answer.answer);
        const sources = formatSourcesForExcel(answer.sources);
        
        excelData.push([
            currentQuestions[index],
            comment,
            cleanAnswer,
            (answer.confidence_score * 100).toFixed(1),
            (answer.fuzzy_score * 100).toFixed(1),
            sources
        ]);
    });
    
    // Create worksheet from data
    const ws = XLSX.utils.aoa_to_sheet(excelData);
    
    // Set column widths for better readability
    ws['!cols'] = [
        { wch: 40 }, // Frage
        { wch: 30 }, // Kommentar zur Antwort
        { wch: 50 }, // Antwort
        { wch: 20 }, // Vector Distance Metric
        { wch: 20 }, // Text Pattern Match
        { wch: 60 }  // Quellen
    ];
    
    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(wb, ws, 'Antworten auf Anfragen');
    
    // Generate Excel file and download
    const fileName = `antworten_${new Date().toISOString().split('T')[0]}.xlsx`;
    XLSX.writeFile(wb, fileName);
    
    showAlert('Excel-Datei erfolgreich exportiert', 'success');
}

// Clear all data
async function clearAllData() {
    if (!confirm('Sind Sie sicher, dass Sie alle historischen Q&A-Daten löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.')) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/clear-data', {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        showAlert(result.message, 'success');
        
        loadStatistics(); // Refresh statistics
        loadCategories(); // Refresh categories
        
    } catch (error) {
        showAlert('Fehler beim Löschen der Daten: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Utility functions
function getConfidenceClass(score) {
    if (score >= 0.7) return 'high';
    if (score >= 0.4) return 'medium';
    return 'low';
}

function getFuzzyClass(score) {
    if (score >= 0.8) return 'high';
    if (score >= 0.6) return 'medium';
    return 'low';
}

function separateCommentAndAnswer(fullAnswer) {
    // Patterns that typically indicate commentary/context before the main answer
    const commentPatterns = [
        // German commentary patterns
        /^(Basierend auf.*?(?:\.|:))\s*(.*)/s,
        /^(Aufgrund.*?(?:\.|:))\s*(.*)/s,
        /^(Laut.*?(?:\.|:))\s*(.*)/s,
        /^(Gemäß.*?(?:\.|:))\s*(.*)/s,
        /^(Entsprechend.*?(?:\.|:))\s*(.*)/s,
        /^(Unter Berücksichtigung.*?(?:\.|:))\s*(.*)/s,
        /^(Nach.*?(?:\.|:))\s*(.*)/s,
        /^(Anhand.*?(?:\.|:))\s*(.*)/s,
        /^(Durch.*?(?:\.|:))\s*(.*)/s,
        /^(Mit Blick auf.*?(?:\.|:))\s*(.*)/s,
        
        // English commentary patterns (legacy support)
        /^(Based on.*?(?:\.|:))\s*(.*)/s,
        /^(According to.*?(?:\.|:))\s*(.*)/s,
        /^(From the historical data.*?(?:\.|:))\s*(.*)/s,
        /^(Our previous experience shows.*?(?:\.|:))\s*(.*)/s,
        /^(The sources indicate.*?(?:\.|:))\s*(.*)/s,
        /^(Looking at similar projects.*?(?:\.|:))\s*(.*)/s,
        
        // German AI response patterns
        /^(Hier ist (?:die|eine) (?:umfassende )?Antwort.*?(?:\.|:))\s*(.*)/si,
        /^(Hier finden Sie (?:die|eine) (?:umfassende )?Antwort.*?(?:\.|:))\s*(.*)/si,
        /^(Ich erstelle (?:eine|die) (?:umfassende )?Antwort.*?(?:\.|:))\s*(.*)/si,
        /^(Dies ist (?:die|eine) (?:umfassende )?Antwort.*?(?:\.|:))\s*(.*)/si,
        /^(Folgende Antwort.*?(?:\.|:))\s*(.*)/si,
        
        // English AI response patterns (legacy support)
        /^(Here is (?:the|a) (?:comprehensive )?answer.*?(?:\.|:))\s*(.*)/si,
        /^(Here's (?:the|a) (?:comprehensive )?answer.*?(?:\.|:))\s*(.*)/si,
        /^(I'll provide (?:a|the) (?:comprehensive )?answer.*?(?:\.|:))\s*(.*)/si,
        /^(This is (?:the|a) (?:comprehensive )?answer.*?(?:\.|:))\s*(.*)/si,
        
        // German markdown formatting
        /^\*\*Antwort\*\*\s*:?\s*(.*)/s,
        /^\*\*Lösung\*\*\s*:?\s*(.*)/s,
        /^Antwort\s*:?\s*(.*)/s,
        /^Lösung\s*:?\s*(.*)/s,
        
        // English markdown formatting (legacy support)
        /^\*\*Answer\*\*\s*:?\s*(.*)/s,
        /^\*\*Response\*\*\s*:?\s*(.*)/s,
        /^Answer\s*:?\s*(.*)/s,
        /^Response\s*:?\s*(.*)/s
    ];
    
    let workingText = fullAnswer;
    let comments = [];
    
    // Process multiple patterns
    for (const pattern of commentPatterns) {
        const match = workingText.match(pattern);
        if (match) {
            if (match[1]) {
                // Clean up markdown and formatting from comment
                const cleanComment = match[1].replace(/\*\*/g, '').trim();
                if (cleanComment && cleanComment.length > 0) {
                    comments.push(cleanComment);
                }
            }
            workingText = match[2] ? match[2].trim() : match[1].trim();
            break; // Take first match
        }
    }
    
    // Clean up the answer text - remove markdown formatting
    let cleanAnswer = workingText
        .replace(/^\*\*.*?\*\*\s*:?\s*/g, '') // Remove **text** at start
        .replace(/\*\*(.*?)\*\*/g, '$1') // Remove **bold** formatting
        .trim();
    
    return {
        comment: comments.join(' '),
        answer: cleanAnswer
    };
}

function formatSourcesForExcel(sources) {
    if (!sources || sources.length === 0) {
        return 'Keine Quellen';
    }
    
    return sources.map((source, index) => 
        `Source ${index + 1}: ${source.question_text.substring(0, 100)}${source.question_text.length > 100 ? '...' : ''}`
    ).join(' | ');
}

function showLoading() {
    document.getElementById('loading-overlay').classList.add('show');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('show');
}

function showAlert(message, type) {
    // Remove existing alerts
    document.querySelectorAll('.alert').forEach(alert => {
        if (!alert.closest('.card')) {
            alert.remove();
        }
    });
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${type}`;
    alertDiv.textContent = message;
    
    // Insert at the top of the container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}