// DatasetDoctor Web UI - Modern JavaScript with Animations

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Disable submit button
    const submitBtn = document.querySelector('.btn-primary');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<svg class="btn-icon" viewBox="0 0 24 24" fill="none"><path d="M12 2V6M12 18V22M4 12H8M16 12H20M19.07 19.07L16.24 16.24M19.07 4.93L16.24 7.76M4.93 19.07L7.76 16.24M4.93 4.93L7.76 7.76" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>Processing...';
    
    // Hide upload section and show loading immediately
    const uploadSection = document.querySelector('.upload-section');
    uploadSection.style.opacity = '0.5';
    uploadSection.style.pointerEvents = 'none';
    
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    
    // Reset progress steps
    resetProgressSteps();
    updateLoadingStep('ingest', 'Analyzing Data Structure...');
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            let errorMsg = data.error || 'Processing failed';
            if (data.issues && data.issues.length > 0) {
                errorMsg += '\n\nIssues found:\n' + data.issues.map((i, idx) => `${idx + 1}. ${i}`).join('\n');
            }
            showError(errorMsg);
            return;
        }
        
        if (data.success) {
            // Simulate progress updates
            setTimeout(() => updateLoadingStep('ingest', 'Loading dataset...'), 300);
            setTimeout(() => updateLoadingStep('scan', 'Scanning for issues...'), 1000);
            setTimeout(() => updateLoadingStep('fix', 'Applying fixes...'), 1800);
            setTimeout(() => updateLoadingStep('validate', 'Validating fixes...'), 2600);
            setTimeout(() => {
                updateLoadingStep('report', 'Generating reports...');
                setTimeout(() => {
                    document.getElementById('loading').classList.add('hidden');
                    uploadSection.style.opacity = '1';
                    uploadSection.style.pointerEvents = 'auto';
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<svg class="btn-icon" viewBox="0 0 24 24" fill="none"><path d="M14.7 6.3C14.5 6.1 14.3 6 14 6C13.7 6 13.5 6.1 13.3 6.3L8.3 11.3C8.1 11.5 8 11.7 8 12C8 12.3 8.1 12.5 8.3 12.7L13.3 17.7C13.5 17.9 13.7 18 14 18C14.3 18 14.5 17.9 14.7 17.7C15.1 17.3 15.1 16.7 14.7 16.3L10.4 12L14.7 7.7C15.1 7.3 15.1 6.7 14.7 6.3Z" fill="white"/></svg>Process Dataset';
                    showResults(data);
                }, 800);
            }, 3400);
        } else {
            uploadSection.style.opacity = '1';
            uploadSection.style.pointerEvents = 'auto';
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<svg class="btn-icon" viewBox="0 0 24 24" fill="none"><path d="M14.7 6.3C14.5 6.1 14.3 6 14 6C13.7 6 13.5 6.1 13.3 6.3L8.3 11.3C8.1 11.5 8 11.7 8 12C8 12.3 8.1 12.5 8.3 12.7L13.3 17.7C13.5 17.9 13.7 18 14 18C14.3 18 14.5 17.9 14.7 17.7C15.1 17.3 15.1 16.7 14.7 16.3L10.4 12L14.7 7.7C15.1 7.3 15.1 6.7 14.7 6.3Z" fill="white"/></svg>Process Dataset';
            document.getElementById('loading').classList.add('hidden');
            let errorMsg = data.error || 'Processing failed';
            if (data.issues && data.issues.length > 0) {
                errorMsg += '\n\nIssues:\n' + data.issues.map((i, idx) => `${idx + 1}. ${i}`).join('\n');
            }
            showError(errorMsg);
        }
    } catch (error) {
        uploadSection.style.opacity = '1';
        uploadSection.style.pointerEvents = 'auto';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<svg class="btn-icon" viewBox="0 0 24 24" fill="none"><path d="M14.7 6.3C14.5 6.1 14.3 6 14 6C13.7 6 13.5 6.1 13.3 6.3L8.3 11.3C8.1 11.5 8 11.7 8 12C8 12.3 8.1 12.5 8.3 12.7L13.3 17.7C13.5 17.9 13.7 18 14 18C14.3 18 14.5 17.9 14.7 17.7C15.1 17.3 15.1 16.7 14.7 16.3L10.4 12L14.7 7.7C15.1 7.3 15.1 6.7 14.7 6.3Z" fill="white"/></svg>Process Dataset';
        document.getElementById('loading').classList.add('hidden');
        showError('Network error: ' + error.message);
    }
});

function showResults(data) {
    // Ensure values are valid numbers and non-negative for counts
    const qualityScore = Math.max(0, Math.min(100, parseFloat(data.quality_score) || 0));
    const totalIssues = Math.max(0, parseInt(data.total_issues) || 0);
    const totalFixes = Math.max(0, parseInt(data.total_fixes) || 0);
    
    // Animate quality score
    animateValue('qualityScore', 0, qualityScore, 1500);
    
    // Update quality progress bar
    setTimeout(() => {
        const progressBar = document.getElementById('qualityProgress');
        if (progressBar) {
            progressBar.style.width = qualityScore + '%';
        }
    }, 100);
    
    // Animate other values (ensure non-negative)
    animateValue('totalIssues', 0, totalIssues, 800);
    animateValue('totalFixes', 0, totalFixes, 800);
    
    // Update dataset info
    document.getElementById('datasetName').textContent = data.dataset_name;
    const [rows, cols] = data.shape;
    document.getElementById('datasetRows').textContent = rows.toLocaleString();
    document.getElementById('datasetCols').textContent = cols;
    
    // Calculate file size (rough estimate) and format appropriately
    const estimatedSizeBytes = rows * cols * 10; // Rough estimate: 10 bytes per cell
    const formattedSize = formatFileSize(estimatedSizeBytes);
    document.getElementById('datasetSize').textContent = formattedSize;
    
    // Update issues subtitle
    if (data.total_issues > 0) {
        document.getElementById('issuesSubtitle').textContent = `Across ${data.columns.length} columns`;
    }
    
    // Set up download links
    const reportFiles = data.report_files || {};
    if (reportFiles.cleaned_dataset) {
        const cleanedFile = reportFiles.cleaned_dataset.split('/').pop();
        document.getElementById('downloadCleaned').href = `/download/${cleanedFile}`;
        document.getElementById('downloadCleaned').style.display = 'flex';
    }
    if (reportFiles.python_script) {
        const scriptFile = reportFiles.python_script.split('/').pop();
        document.getElementById('downloadScript').href = `/download/${scriptFile}`;
        document.getElementById('downloadScript').style.display = 'flex';
    }
    if (reportFiles.json_report) {
        const jsonFile = reportFiles.json_report.split('/').pop();
        document.getElementById('downloadJSON').href = `/download/${jsonFile}`;
        document.getElementById('downloadJSON').style.display = 'flex';
    }
    if (reportFiles.html_report) {
        const htmlFile = reportFiles.html_report.split('/').pop();
        document.getElementById('viewHTML').href = `/report/${htmlFile}`;
        document.getElementById('viewHTML').style.display = 'flex';
    }
    
    // Show cleaned file notice if applicable
    if (data.is_cleaned_file && data.cleaned_file_note) {
        const notice = document.getElementById('cleanedFileNotice');
        const noteText = document.getElementById('cleanedFileNote');
        if (notice && noteText) {
            noteText.textContent = data.cleaned_file_note;
            notice.style.display = 'block';
            
            // Animate notice entrance
            if (typeof anime !== 'undefined') {
                anime({
                    targets: notice,
                    opacity: [0, 1],
                    translateY: [-10, 0],
                    duration: 500,
                    easing: 'easeOutExpo'
                });
            }
        }
    }
    
    // Show issues log if available
    if (data.issues && data.issues.length > 0) {
        displayIssues(data.issues);
    }
    
    // Show results with animation
    document.getElementById('results').classList.remove('hidden');
    
    // Animate cards entrance
    if (typeof anime !== 'undefined') {
        anime({
            targets: '.card',
            opacity: [0, 1],
            translateY: [30, 0],
            delay: anime.stagger(100),
            duration: 600,
            easing: 'easeOutExpo'
        });
    }
}

function animateValue(elementId, start, end, duration) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Ensure end is a valid number and not negative (for counts)
    if (isNaN(end) || end < 0) {
        end = 0;
    }
    
    // If start and end are the same, just set the value immediately
    if (start === end) {
        if (elementId === 'qualityScore') {
            element.textContent = Math.round(end);
        } else {
            element.textContent = Math.max(0, Math.round(end)); // Ensure non-negative for counts
        }
        return;
    }
    
    const range = Math.abs(end - start);
    const increment = end > start ? 1 : -1;
    
    // Ensure stepTime is at least 1ms and not too small
    // Cap the range to prevent extremely fast animations
    const maxRange = 1000; // Max steps for smooth animation
    const adjustedRange = Math.min(range, maxRange);
    const stepTime = Math.max(1, Math.floor(duration / adjustedRange));
    
    let current = start;
    let stepCount = 0;
    const maxSteps = range + 10; // Safety limit to prevent infinite loops
    
    const timer = setInterval(() => {
        stepCount++;
        
        // Safety check: prevent infinite loops
        if (stepCount > maxSteps) {
            clearInterval(timer);
            // Set final value
            if (elementId === 'qualityScore') {
                element.textContent = Math.round(end);
            } else {
                element.textContent = Math.max(0, Math.round(end));
            }
            return;
        }
        
        // Calculate current value based on progress
        const progress = stepCount / adjustedRange;
        current = start + (end - start) * Math.min(progress, 1);
        
        // Update display
        if (elementId === 'qualityScore') {
            element.textContent = Math.round(current);
        } else {
            // For counts (issues, fixes), ensure non-negative
            element.textContent = Math.max(0, Math.round(current));
        }
        
        // Check if we've reached the end
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end) || Math.abs(current - end) < 0.5) {
            clearInterval(timer);
            // Set final value to ensure accuracy
            if (elementId === 'qualityScore') {
                element.textContent = Math.round(end);
            } else {
                element.textContent = Math.max(0, Math.round(end));
            }
        }
    }, stepTime);
}

function resetProgressSteps() {
    const steps = ['ingest', 'scan', 'fix', 'validate', 'report'];
    const stepNumbers = [1, 2, 3, 4, 5];
    
    steps.forEach((step, index) => {
        const stepEl = document.getElementById(`step-${step}`);
        if (stepEl) {
            stepEl.classList.remove('active', 'completed', 'pending');
            stepEl.classList.add('pending');
            
            // Reset to show number
            const numberEl = stepEl.querySelector('.step-number');
            const checkEl = stepEl.querySelector('.step-check');
            
            if (numberEl) {
                numberEl.textContent = stepNumbers[index];
                numberEl.style.display = 'flex';
            }
            if (checkEl) {
                checkEl.style.display = 'none';
            }
        }
    });
}

function updateLoadingStep(step, text) {
    const stepEl = document.getElementById(`step-${step}`);
    if (stepEl) {
        // Mark previous steps as completed
        const steps = ['ingest', 'scan', 'fix', 'validate', 'report'];
        const currentIndex = steps.indexOf(step);
        steps.slice(0, currentIndex).forEach(s => {
            const prevStep = document.getElementById(`step-${s}`);
            if (prevStep) {
                prevStep.classList.remove('active', 'pending');
                prevStep.classList.add('completed');
                
                // Animate number to checkmark
                const numberEl = prevStep.querySelector('.step-number');
                const checkEl = prevStep.querySelector('.step-check');
                
                if (numberEl && checkEl) {
                    // Hide number, show checkmark with animation
                    if (typeof anime !== 'undefined') {
                        anime({
                            targets: numberEl,
                            scale: [1, 0],
                            opacity: [1, 0],
                            duration: 200,
                            easing: 'easeInExpo',
                            complete: () => {
                                numberEl.style.display = 'none';
                                checkEl.style.display = 'flex';
                                anime({
                                    targets: checkEl,
                                    scale: [0, 1],
                                    opacity: [0, 1],
                                    duration: 300,
                                    easing: 'easeOutExpo'
                                });
                            }
                        });
                    } else {
                        numberEl.style.display = 'none';
                        checkEl.style.display = 'flex';
                    }
                }
            }
        });
        
        // Mark current step as active
        stepEl.classList.remove('pending', 'completed');
        stepEl.classList.add('active');
        
        // Ensure number is visible for active step
        const numberEl = stepEl.querySelector('.step-number');
        const checkEl = stepEl.querySelector('.step-check');
        if (numberEl) {
            numberEl.style.display = 'flex';
        }
        if (checkEl) {
            checkEl.style.display = 'none';
        }
        
        // Animate step activation
        if (typeof anime !== 'undefined') {
            anime({
                targets: stepEl,
                scale: [0.8, 1],
                opacity: [0.5, 1],
                duration: 400,
                easing: 'easeOutExpo'
            });
        }
    }
    
    if (text) {
        document.getElementById('loadingText').textContent = text;
    }
}

function displayIssues(issues) {
    const issuesSection = document.getElementById('issuesLogSection');
    const issuesList = document.getElementById('issuesList');
    issuesList.innerHTML = '';
    
    // Update priority badge
    const criticalCount = issues.filter(i => i.severity === 'critical' || i.severity === 'high').length;
    const priorityBadge = document.getElementById('priorityBadge');
    if (priorityBadge) {
        priorityBadge.textContent = `${criticalCount} High Priority`;
    }
    
    issues.forEach((issue, index) => {
        const issueItem = document.createElement('div');
        issueItem.className = 'issue-item';
        
        // Get icon based on issue type
        let icon = '⚠️';
        if (issue.type === 'missing_values') icon = '🔗';
        else if (issue.type === 'type_inconsistency') icon = '📅';
        else if (issue.type === 'duplicates') icon = '📋';
        else if (issue.type === 'outliers') icon = '📊';
        
        // Build issue HTML with AI insight if available
        let aiInsightHTML = '';
        if (issue.gemini_insight && issue.gemini_insight.trim()) {
            aiInsightHTML = `
                <div class="ai-insight">
                    <div class="ai-insight-header">
                        <span class="ai-icon">🤖</span>
                        <span class="ai-label">AI Insight</span>
                    </div>
                    <div class="ai-insight-text">${escapeHtml(issue.gemini_insight)}</div>
                </div>
            `;
        }
        
        issueItem.innerHTML = `
            <div class="issue-icon">${icon}</div>
            <div class="issue-content">
                <div class="issue-title">${issue.type ? issue.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Issue'} in '${issue.column || 'Unknown'}'</div>
                <div class="issue-description">${issue.description || issue}</div>
                ${aiInsightHTML}
                <div class="issue-action">${getFixAction(issue)}</div>
                <div class="issue-status">Fixed</div>
            </div>
        `;
        
        issuesList.appendChild(issueItem);
        
        // Animate entrance
        if (typeof anime !== 'undefined') {
            anime({
                targets: issueItem,
                opacity: [0, 1],
                translateX: [-20, 0],
                delay: index * 100,
                duration: 500,
                easing: 'easeOutExpo'
            });
        }
    });
    
    issuesSection.style.display = 'block';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    // Round to 2 decimal places, but show integers if no decimals needed
    const size = bytes / Math.pow(k, i);
    const rounded = Math.round(size * 100) / 100;
    
    // If it's a whole number, show without decimals
    if (rounded % 1 === 0) {
        return rounded + ' ' + sizes[i];
    }
    
    return rounded.toFixed(2) + ' ' + sizes[i];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getFixAction(issue) {
    if (issue.type === 'missing_values') {
        return 'Imputed with median/mode';
    } else if (issue.type === 'type_inconsistency') {
        return 'Converted to correct type';
    } else if (issue.type === 'duplicates') {
        return 'Removed duplicates';
    } else if (issue.type === 'outliers') {
        return 'Handled outliers';
    }
    return 'Auto-fixed';
}

function showError(message) {
    const errorEl = document.getElementById('error');
    const errorMsg = document.getElementById('errorMessage');
    errorMsg.textContent = message;
    errorEl.classList.remove('hidden');
    
    // Animate error
    if (typeof anime !== 'undefined') {
        anime({
            targets: errorEl,
            opacity: [0, 1],
            translateY: [-10, 0],
            duration: 500,
            easing: 'easeOutExpo'
        });
    }
}

// Update file input label when file is selected
document.getElementById('fileInput').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const label = document.querySelector('.upload-text-primary');
        if (label) {
            label.textContent = `Selected: ${file.name}`;
            label.style.color = '#7C3AED';
        }
    }
});

// Make Browse Files button work
document.querySelector('.btn-browse')?.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('fileInput').click();
});

// Drag and drop functionality
const uploadLabel = document.querySelector('.upload-label');
if (uploadLabel) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadLabel.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadLabel.addEventListener(eventName, () => {
            uploadLabel.style.borderColor = '#7C3AED';
            uploadLabel.style.background = '#F3E8FF';
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadLabel.addEventListener(eventName, () => {
            uploadLabel.style.borderColor = '';
            uploadLabel.style.background = '';
        }, false);
    });
    
    uploadLabel.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            document.getElementById('fileInput').files = files;
            const label = document.querySelector('.upload-text-primary');
            if (label) {
                label.textContent = `Selected: ${files[0].name}`;
                label.style.color = '#7C3AED';
            }
        }
    }, false);
}

// Initialize animations on page load
document.addEventListener('DOMContentLoaded', () => {
    if (typeof anime !== 'undefined') {
        // Animate header
        anime({
            targets: 'header',
            opacity: [0, 1],
            translateY: [-20, 0],
            duration: 800,
            easing: 'easeOutExpo'
        });
        
        // Animate upload section
        anime({
            targets: '.upload-section',
            opacity: [0, 1],
            translateY: [20, 0],
            delay: 200,
            duration: 800,
            easing: 'easeOutExpo'
        });
    }
});
