import { useState, useEffect } from 'react';
import { ticketsAPI } from '../api';

function Dashboard({ user, onLogout }) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    student_name: '',
    location: '',
    issue_type: '',
    description: '',
    image: null,
  });
  const [imagePreview, setImagePreview] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadTickets();
  }, []);

  const loadTickets = async () => {
    try {
      const response = await ticketsAPI.getAllTickets();
      setTickets(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load tickets');
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData({ ...formData, image: file });
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.image) {
      setError('Please select an image');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('student_name', formData.student_name);
      formDataToSend.append('location', formData.location);
      formDataToSend.append('issue_type', formData.issue_type);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('image', formData.image);

      const response = await ticketsAPI.createTicket(formDataToSend);
      
      setSuccess(`Ticket #${response.data.id} created successfully! Issue: ${response.data.issue_type}`);
      setFormData({ student_name: '', location: '', issue_type: '', description: '', image: null });
      setImagePreview('');
      setShowCreateForm(false);
      loadTickets();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create ticket');
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateString) => {
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
      return date.toLocaleDateString();
    }
  };

  return (
    <div>
      <div className="header">
        <h1>🔧 AI Maintenance Reporter</h1>
        <div className="user-info">
          <span>Welcome, {user.full_name}!</span>
          <button className="btn btn-logout" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>

      <div className="container">
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2>📸 Report an Issue</h2>
            <button
              className="btn btn-primary"
              onClick={() => setShowCreateForm(!showCreateForm)}
              style={{ width: 'auto' }}
            >
              {showCreateForm ? 'Cancel' : 'New Report'}
            </button>
          </div>

          {showCreateForm && (
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="student_name">Your Name</label>
                <input
                  type="text"
                  id="student_name"
                  value={formData.student_name}
                  onChange={(e) => setFormData({ ...formData, student_name: e.target.value })}
                  placeholder="Enter your name"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="location">Location</label>
                <input
                  type="text"
                  id="location"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="e.g., Room 101, Building A"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="issue_type">Issue Type</label>
                <select
                  id="issue_type"
                  value={formData.issue_type}
                  onChange={(e) => setFormData({ ...formData, issue_type: e.target.value })}
                  required
                >
                  <option value="">Select issue type</option>
                  <option value="Electrical">⚡ Electrical</option>
                  <option value="Plumbing">🚰 Plumbing</option>
                  <option value="HVAC">❄️ HVAC</option>
                  <option value="Structural">🏗️ Structural</option>
                  <option value="Furniture">🪑 Furniture</option>
                  <option value="Cleaning">🧹 Cleaning</option>
                  <option value="IT Equipment">💻 IT Equipment</option>
                  <option value="Safety">⚠️ Safety</option>
                  <option value="Other">📦 Other</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe the issue in detail..."
                  rows="4"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="image">Upload Photo</label>
                <div className="file-upload-wrapper">
                  <input
                    type="file"
                    id="image"
                    accept="image/*"
                    onChange={handleFileChange}
                    required
                  />
                  <label htmlFor="image" className="file-upload-label">
                    <span>📁</span>
                    <span>{formData.image ? formData.image.name : 'Choose an image'}</span>
                  </label>
                </div>
                {imagePreview && (
                  <div className="image-preview">
                    <img src={imagePreview} alt="Preview" />
                  </div>
                )}
              </div>

              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? 'Submitting...' : 'Submit Report'}
              </button>
            </form>
          )}
        </div>

        <div className="card">
          <h2>📋 Recent Tickets</h2>
          {loading ? (
            <div className="loading">Loading tickets...</div>
          ) : tickets.length === 0 ? (
            <div className="loading">No tickets found. Create your first report!</div>
          ) : (
            <div className="tickets-grid">
              {tickets.map((ticket) => (
                <div key={ticket.id} className="ticket-card">
                  <div className="ticket-header">
                    <span className="ticket-id">#{ticket.id}</span>
                    <span className={`priority-badge priority-${ticket.priority}`}>
                      {ticket.priority}
                    </span>
                  </div>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong>👤 Student:</strong> {ticket.student_name}
                  </div>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong>📍 Location:</strong> {ticket.location}
                  </div>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong>🔧 Issue:</strong> {ticket.issue_type}
                  </div>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong>📅 Created:</strong> {formatDate(ticket.created_at)}
                  </div>
                  <div
                    style={{
                      background: 'white',
                      padding: '0.75rem',
                      borderRadius: '6px',
                      marginTop: '0.75rem',
                      fontSize: '0.875rem',
                      color: '#64748b',
                      lineHeight: '1.5',
                    }}
                  >
                    <strong>Description:</strong>
                    <br />
                    {ticket.description}
                  </div>
                  <span className={`status-badge status-${ticket.status}`}>
                    {ticket.status.replace('_', ' ')}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
