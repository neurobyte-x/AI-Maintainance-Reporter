// API Base URL
const API_BASE_URL = 'http://localhost:8000/api';

// DOM Elements
const ticketForm = document.getElementById('ticketForm');
const imageUpload = document.getElementById('imageUpload');
const imagePreview = document.getElementById('imagePreview');
const submitBtn = document.getElementById('submitBtn');
const resultMessage = document.getElementById('resultMessage');
const ticketsList = document.getElementById('ticketsList');
const refreshBtn = document.getElementById('refreshBtn');
const uploadText = document.querySelector('.upload-text');

// Image preview handler
imageUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            imagePreview.innerHTML = `<img src="${event.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
        uploadText.textContent = file.name;
    }
});

// Form submission handler
ticketForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data
    const formData = new FormData();
    const studentName = document.getElementById('studentName').value;
    const location = document.getElementById('location').value;
    const imageFile = imageUpload.files[0];
    
    if (!imageFile) {
        showMessage('Please select an image', 'error');
        return;
    }
    
    formData.append('student_name', studentName);
    formData.append('location', location);
    formData.append('image', imageFile);
    
    // Disable button and show loading
    submitBtn.disabled = true;
    document.querySelector('.btn-text').style.display = 'none';
    document.querySelector('.spinner').style.display = 'inline-block';
    resultMessage.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE_URL}/tickets`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to create ticket');
        }
        
        const data = await response.json();
        
        showMessage(
            `✅ Ticket #${data.ticket_id} created successfully! Issue detected: ${data.issue_type} (Priority: ${data.priority})`,
            'success'
        );
        
        // Reset form
        ticketForm.reset();
        imagePreview.innerHTML = '';
        uploadText.textContent = 'Choose an image';
        
        // Refresh tickets list
        loadTickets();
        
    } catch (error) {
        showMessage(`❌ Error: ${error.message}`, 'error');
    } finally {
        // Re-enable button
        submitBtn.disabled = false;
        document.querySelector('.btn-text').style.display = 'inline';
        document.querySelector('.spinner').style.display = 'none';
    }
});

// Load tickets function
async function loadTickets() {
    ticketsList.innerHTML = '<p class="loading">Loading tickets...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/tickets`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch tickets');
        }
        
        const tickets = await response.json();
        
        if (tickets.length === 0) {
            ticketsList.innerHTML = '<p class="loading">No tickets found. Submit your first report!</p>';
            return;
        }
        
        ticketsList.innerHTML = tickets.map(ticket => `
            <div class="ticket-card">
                <div class="ticket-header">
                    <span class="ticket-id">#${ticket.ticket_id}</span>
                    <span class="ticket-priority priority-${ticket.priority}">${ticket.priority}</span>
                </div>
                <div class="ticket-info">
                    <strong>👤 Student:</strong> ${ticket.student_name}
                </div>
                <div class="ticket-info">
                    <strong>📍 Location:</strong> ${ticket.location}
                </div>
                <div class="ticket-info">
                    <strong>🔧 Issue Type:</strong> ${ticket.issue_type}
                </div>
                <div class="ticket-info">
                    <strong>📅 Created:</strong> ${formatDate(ticket.created_at)}
                </div>
                <div class="ticket-description">
                    <strong>Description:</strong><br>
                    ${ticket.description}
                </div>
                <span class="ticket-status status-${ticket.status}">${ticket.status.replace('_', ' ')}</span>
            </div>
        `).join('');
        
    } catch (error) {
        ticketsList.innerHTML = `<p class="loading" style="color: red;">Error loading tickets: ${error.message}</p>`;
    }
}

// Show message function
function showMessage(message, type) {
    resultMessage.textContent = message;
    resultMessage.className = `result-message ${type}`;
    resultMessage.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        resultMessage.style.display = 'none';
    }, 5000);
}

// Format date function
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
        const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
        if (diffHours === 0) {
            const diffMinutes = Math.floor(diffTime / (1000 * 60));
            return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
        }
        return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else {
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Refresh button handler
refreshBtn.addEventListener('click', () => {
    loadTickets();
});

// Load tickets on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTickets();
});

// Auto-refresh tickets every 30 seconds
setInterval(loadTickets, 30000);
