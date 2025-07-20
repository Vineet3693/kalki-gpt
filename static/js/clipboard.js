
// Clipboard functionality for Kalki GPT

document.addEventListener('DOMContentLoaded', function() {
    // Add copy buttons to Sanskrit verses
    addCopyButtons();
    
    // Initialize clipboard functionality
    initClipboard();
});

function addCopyButtons() {
    const sanskritElements = document.querySelectorAll('.sanskrit-text, .sanskrit-verse, .sanskrit-sloka');
    
    sanskritElements.forEach((element, index) => {
        if (!element.querySelector('.copy-button')) {
            const copyButton = document.createElement('button');
            copyButton.className = 'copy-button';
            copyButton.innerHTML = '📋 Copy';
            copyButton.setAttribute('data-copy-target', `sanskrit-${index}`);
            
            // Add ID to target element
            element.setAttribute('id', `sanskrit-${index}`);
            
            // Style the button
            copyButton.style.cssText = `
                position: absolute;
                top: 10px;
                right: 10px;
                background: #FF6B35;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 0.8em;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            
            // Make parent relative
            element.style.position = 'relative';
            
            // Show button on hover
            element.addEventListener('mouseenter', () => {
                copyButton.style.opacity = '1';
            });
            
            element.addEventListener('mouseleave', () => {
                copyButton.style.opacity = '0';
            });
            
            element.appendChild(copyButton);
        }
    });
}

function initClipboard() {
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('copy-button')) {
            const targetId = event.target.getAttribute('data-copy-target');
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const textToCopy = targetElement.textContent || targetElement.innerText;
                
                // Use modern clipboard API if available
                if (navigator.clipboard && window.isSecureContext) {
                    navigator.clipboard.writeText(textToCopy).then(() => {
                        showCopySuccess(event.target);
                    }).catch(err => {
                        console.error('Failed to copy text: ', err);
                        fallbackCopyTextToClipboard(textToCopy, event.target);
                    });
                } else {
                    // Fallback for older browsers
                    fallbackCopyTextToClipboard(textToCopy, event.target);
                }
            }
        }
    });
}

function fallbackCopyTextToClipboard(text, button) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    
    // Avoid scrolling to bottom
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopySuccess(button);
        } else {
            showCopyError(button);
        }
    } catch (err) {
        console.error('Fallback copy failed: ', err);
        showCopyError(button);
    }
    
    document.body.removeChild(textArea);
}

function showCopySuccess(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '✅ Copied!';
    button.style.background = '#28A745';
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.style.background = '#FF6B35';
    }, 2000);
}

function showCopyError(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '❌ Failed';
    button.style.background = '#DC3545';
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.style.background = '#FF6B35';
    }, 2000);
}

// Share functionality
function shareVerse(text, title = 'Verse from Hindu Scriptures') {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: text,
            url: window.location.href
        }).then(() => {
            console.log('Successfully shared');
        }).catch((error) => {
            console.log('Error sharing:', error);
            fallbackShare(text, title);
        });
    } else {
        fallbackShare(text, title);
    }
}

function fallbackShare(text, title) {
    const shareData = `${title}\n\n${text}\n\nShared from Kalki GPT: ${window.location.href}`;
    
    // Try to copy to clipboard as fallback
    if (navigator.clipboard) {
        navigator.clipboard.writeText(shareData).then(() => {
            alert('Content copied to clipboard! You can now paste and share it.');
        });
    } else {
        // Create a modal with shareable text
        showShareModal(shareData);
    }
}

function showShareModal(text) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: white;
        padding: 2rem;
        border-radius: 10px;
        max-width: 500px;
        width: 90%;
        max-height: 70%;
        overflow-y: auto;
    `;
    
    modalContent.innerHTML = `
        <h3>Share this content:</h3>
        <textarea readonly style="width: 100%; height: 200px; margin: 1rem 0; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">${text}</textarea>
        <div style="text-align: right;">
            <button onclick="this.closest('[style*=\"position: fixed\"]').remove()" style="background: #FF6B35; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">Close</button>
        </div>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Add share buttons to verses
function addShareButtons() {
    const verses = document.querySelectorAll('.sanskrit-text, .source-card');
    
    verses.forEach((verse, index) => {
        if (!verse.querySelector('.share-button')) {
            const shareButton = document.createElement('button');
            shareButton.className = 'share-button';
            shareButton.innerHTML = '📤 Share';
            shareButton.style.cssText = `
                position: absolute;
                top: 10px;
                right: 60px;
                background: #28A745;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 0.8em;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            
            shareButton.addEventListener('click', () => {
                const text = verse.textContent || verse.innerText;
                shareVerse(text);
            });
            
            verse.style.position = 'relative';
            verse.appendChild(shareButton);
            
            verse.addEventListener('mouseenter', () => {
                shareButton.style.opacity = '1';
            });
            
            verse.addEventListener('mouseleave', () => {
                shareButton.style.opacity = '0';
            });
        }
    });
}

// Initialize share functionality
document.addEventListener('DOMContentLoaded', function() {
    addShareButtons();
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl+C or Cmd+C to copy focused verse
    if ((event.ctrlKey || event.metaKey) && event.key === 'c') {
        const focusedVerse = document.querySelector('.sanskrit-text:hover, .source-card:hover');
        if (focusedVerse) {
            const text = focusedVerse.textContent || focusedVerse.innerText;
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text);
                // Show temporary notification
                showNotification('Verse copied to clipboard!');
            }
        }
    }
});

function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28A745;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        z-index: 1001;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
