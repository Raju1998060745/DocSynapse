// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const messagesContainer = document.getElementById('messages-container');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-btn');
    const attachmentButton = document.getElementById('attachment-btn');
    const fileInput = document.getElementById('file-input');
    const filePreview = document.getElementById('file-preview');
    const fileList = document.getElementById('file-list');
    
    // Files to upload
    let filesToUpload = [];
    
    // Initialize by loading messages
    loadMessages();
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    messageInput.addEventListener('input', updateSendButton);
    
    attachmentButton.addEventListener('click', function() {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', handleFileSelection);
    
    // Functions
    async function loadMessages() {
        try {
            const response = await fetch('/api/messages');
            if (!response.ok) {
                throw new Error('Failed to load messages');
            }
            
            const messages = await response.json();
            messages.forEach(message => {
                appendMessage(message);
            });
            scrollToBottom();
        } catch (error) {
            console.error('Error loading messages:', error);
            showErrorMessage('Failed to load messages. Please refresh the page.');
        }
    }
    
    async function sendMessage() {
        const messageText = messageInput.value.trim();
        
        if (!messageText && filesToUpload.length === 0) {
            return;
        }
        
        // Clear input
        messageInput.value = '';
        updateSendButton();
        
        // Show loading indicator
        appendLoadingIndicator();
        
        let fileIds = [];
        
        try {
            // Send message with file references
            const response = await fetch('/api/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: messageText,
                    fileIds: fileIds,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to send message');
            }
            
            // Clear file preview
            clearFilePreview();
            
            // Process response (bot message will be added by server)
            // No need to manually add it here as we'll reload messages
            await loadMessages();
            
        } catch (error) {
            console.error('Error sending message:', error);
            showErrorMessage('Failed to send message. Please try again.');
        } finally {
            // Remove loading indicator
            removeLoadingIndicator();
            scrollToBottom();
        }
    }
    
    async function handleUploadConfirmation() {
        if (filesToUpload.length === 0) return;
        
        try {
            // Show loading state
            const uploadButton = document.getElementById('upload-confirm-btn');
            if (uploadButton) {
                uploadButton.disabled = true;
                uploadButton.innerHTML = `
                    <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Uploading...
                `;
            }
            
            const formData = new FormData();
            filesToUpload.forEach(file => {
                formData.append('files', file);
            });
            
            const response = await fetch('/api/files/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('File upload failed');
            }
            
            const data = await response.json();
            
            // Show success message
            showSuccessMessage(`${filesToUpload.length} file(s) uploaded successfully`);
            
            // Clear file preview
            clearFilePreview();
            
            return data.fileIds || [];
        } catch (error) {
            console.error('Error uploading files:', error);
            showErrorMessage('Failed to upload files. Please try again.');
            return [];
        }
    }
    
    function handleFileSelection(e) {
        if (e.target.files && e.target.files.length > 0) {
            const newFiles = Array.from(e.target.files);
            filesToUpload = [...filesToUpload, ...newFiles];
            
            // Show file preview
            updateFilePreview();
        }
    }
    
    function updateFilePreview() {
        if (filesToUpload.length === 0) {
            filePreview.classList.add('hidden');
            return;
        }
        
        filePreview.classList.remove('hidden');
        fileList.innerHTML = '';
        
        // Container for file items
        const filesContainer = document.createElement('div');
        filesContainer.className = 'flex flex-wrap gap-2 mb-2';
        
        filesToUpload.forEach((file, index) => {
            const fileElement = document.createElement('div');
            fileElement.className = 'flex items-center bg-slate-100 rounded-full px-3 py-1';
            fileElement.innerHTML = `
                <span class="text-xs text-slate-700 mr-1 truncate max-w-xs">${file.name}</span>
                <button class="text-slate-400 hover:text-red-500 file-remove" data-index="${index}">
                    <i data-feather="trash-2" width="14"></i>
                </button>
            `;
            filesContainer.appendChild(fileElement);
        });
        
        fileList.appendChild(filesContainer);
        
        // Add upload confirmation button
        const uploadButton = document.createElement('div');
        uploadButton.className = 'flex justify-end';
        uploadButton.innerHTML = `
            <button id="upload-confirm-btn" class="bg-indigo-700 hover:bg-indigo-800 text-white text-xs px-4 py-2 rounded-md flex items-center">
                <i data-feather="upload-cloud" width="14" class="mr-2"></i>
                Upload Files
            </button>
        `;
        fileList.appendChild(uploadButton);
        
        // Reinitialize Feather icons
        feather.replace();
        
        // Add event listeners to remove buttons
        document.querySelectorAll('.file-remove').forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                removeFile(index);
            });
        });
        
        // Add event listener to upload confirmation button
        document.getElementById('upload-confirm-btn').addEventListener('click', handleUploadConfirmation);
        
        updateSendButton();
    }
    
    function removeFile(index) {
        filesToUpload = filesToUpload.filter((_, i) => i !== index);
        updateFilePreview();
    }
    
    function clearFilePreview() {
        filesToUpload = [];
        fileList.innerHTML = '';
        filePreview.classList.add('hidden');
    }
    
    function appendMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `mb-4 flex ${message.sender === 'human' ? 'justify-end' : 'justify-start'}`;
        
        let avatarHtml = '';
        if (message.sender === 'ai') {
            avatarHtml = `
                <div class="h-8 w-8 rounded-full bg-indigo-800 flex items-center justify-center mr-2 mt-1">
                    <span class="text-white text-xs font-semibold">AI</span>
                </div>
            `;
        }
        
        let messageClass = message.sender === 'human' 
            ? 'bg-indigo-700 text-white rounded-tr-none' 
            : message.isError 
                ? 'bg-red-50 text-red-800 border border-red-200 rounded-tl-none'
                : message.isSuccess
                    ? 'bg-green-50 text-green-800 border border-green-200 rounded-tl-none'
                    : 'bg-white text-slate-800 rounded-tl-none border border-slate-200';
        
        let fileAttachmentsHtml = '';
        if (message.files && message.files.length > 0) {
            fileAttachmentsHtml = `
                <div class="mt-2 text-xs">
                    <p class="font-semibold ${message.sender === 'human' ? 'text-indigo-200' : 'text-indigo-800'}">
                        Attached files:
                    </p>
                    <ul class="mt-1">
                        ${message.files.map(file => `
                            <li class="${message.sender === 'human' ? 'text-indigo-100' : 'text-slate-600'}">
                                ${file.name || 'File'}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        let userAvatarHtml = '';
        if (message.sender === 'human') {
            userAvatarHtml = `
                <div class="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center ml-2 mt-1">
                    <span class="text-white text-xs font-semibold">You</span>
                </div>
            `;
        }
        
        messageElement.innerHTML = `
            ${avatarHtml}
            <div class="max-w-xs md:max-w-md lg:max-w-lg rounded-2xl p-3 shadow-md ${messageClass}">
                <p class="text-sm">${message.text}</p>
                ${fileAttachmentsHtml}
            </div>
            ${userAvatarHtml}
        `;
        
        // Replace the loading indicator if it exists
        const loadingIndicator = messagesContainer.querySelector('.loading-indicator');
        if (loadingIndicator) {
            messagesContainer.replaceChild(messageElement, loadingIndicator);
        } else {
            messagesContainer.appendChild(messageElement);
        }
    }
    
    function appendLoadingIndicator() {
        const loadingElement = document.createElement('div');
        loadingElement.className = 'flex justify-start mb-4 loading-indicator';
        loadingElement.innerHTML = `
            <div class="h-8 w-8 rounded-full bg-indigo-800 flex items-center justify-center mr-2">
                <span class="text-white text-xs font-semibold">AI</span>
            </div>
            <div class="bg-white text-slate-800 rounded-2xl rounded-tl-none p-3 shadow-md border border-slate-200">
                <svg class="animate-spin text-indigo-600" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-dasharray="32" stroke-dashoffset="16" />
                </svg>
            </div>
        `;
        
        messagesContainer.appendChild(loadingElement);
        scrollToBottom();
    }
    
    function removeLoadingIndicator() {
        const loadingIndicator = messagesContainer.querySelector('.loading-indicator');
        if (loadingIndicator) {
            messagesContainer.removeChild(loadingIndicator);
        }
    }
    
    function showErrorMessage(text) {
        const errorMessage = {
            id: Date.now(),
            text: text,
            sender: 'bot',
            isError: true
        };
        appendMessage(errorMessage);
    }
    
    function updateSendButton() {
        if (messageInput.value.trim() || filesToUpload.length > 0) {
            sendButton.classList.remove('bg-slate-200', 'text-slate-400');
            sendButton.classList.add('bg-indigo-700', 'text-white', 'hover:bg-indigo-800', 'shadow-sm');
        } else {
            sendButton.classList.add('bg-slate-200', 'text-slate-400');
            sendButton.classList.remove('bg-indigo-700', 'text-white', 'hover:bg-indigo-800', 'shadow-sm');
        }
    }
    
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});