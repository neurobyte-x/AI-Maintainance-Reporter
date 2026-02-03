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
      formDataToSend.append('image', formData.image);

      const response = await ticketsAPI.createTicket(formDataToSend);
      
      setSuccess(`Ticket #${response.data.id} created successfully! Issue: ${response.data.issue_type}`);
      setFormData({ student_name: '', location: '', image: null });
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

  const getPriorityClasses = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-amber-100 text-amber-800';
      case 'low': return 'bg-emerald-100 text-[#00C896]';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const getStatusClasses = (status) => {
    switch (status) {
      case 'pending': return 'bg-amber-100 text-amber-800';
      case 'in_progress': return 'bg-[#F4EEFF] text-[#6C5CE7]';
      case 'resolved': return 'bg-emerald-100 text-[#00C896]';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white px-8 py-4 shadow-md mb-8 flex justify-between items-center">
        <h1 className="text-[#6C5CE7] text-2xl font-bold"> AI Maintenance Reporter</h1>
        <div className="flex items-center gap-4">
          <span className="text-gray-700">Welcome, {user.full_name}!</span>
          <button 
            className="py-2 px-4 rounded-lg text-sm font-semibold bg-red-500 text-white hover:bg-red-600 transition-colors"
            onClick={onLogout}
          >
            Logout
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-8">
        {error && (
          <div className="bg-red-50 text-red-800 p-3 rounded-lg mb-4 border-l-4 border-red-500">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-emerald-50 text-[#00C896] p-3 rounded-lg mb-4 border-l-4 border-[#00C896]">
            {success}
          </div>
        )}

        {/* Create Report Card */}
        <div className="bg-white rounded-2xl p-8 shadow-xl mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">📸 Report an Issue</h2>
            <button
              className="py-2.5 px-6 rounded-lg font-semibold transition-all duration-300 bg-gradient-primary text-white hover:-translate-y-0.5 hover:shadow-lg"
              onClick={() => setShowCreateForm(!showCreateForm)}
            >
              {showCreateForm ? 'Cancel' : 'New Report'}
            </button>
          </div>

          {showCreateForm && (
            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label htmlFor="student_name" className="block mb-2 font-semibold text-gray-900">
                  Your Name
                </label>
                <input
                  type="text"
                  id="student_name"
                  value={formData.student_name}
                  onChange={(e) => setFormData({ ...formData, student_name: e.target.value })}
                  placeholder="Enter your name"
                  required
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg text-base transition-colors duration-300 focus:outline-none focus:border-[#6C5CE7]"
                />
              </div>

              <div className="mb-6">
                <label htmlFor="location" className="block mb-2 font-semibold text-gray-900">
                  Location
                </label>
                <input
                  type="text"
                  id="location"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="e.g., Room 101, Building A"
                  required
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg text-base transition-colors duration-300 focus:outline-none focus:border-[#6C5CE7]"
                />
              </div>

              <div className="mb-6">
                <label htmlFor="image" className="block mb-2 font-semibold text-gray-900">
                  Upload Photo (AI will analyze the issue)
                </label>
                <div className="relative">
                  <input
                    type="file"
                    id="image"
                    accept="image/*"
                    onChange={handleFileChange}
                    required
                    className="absolute w-px h-px opacity-0 overflow-hidden"
                  />
                  <label 
                    htmlFor="image" 
                    className="flex items-center justify-center gap-2 p-4 border-2 border-dashed border-gray-200 rounded-lg cursor-pointer transition-all duration-300 bg-gray-50 hover:border-[#6C5CE7] hover:bg-gray-100"
                  >
                    <span className="text-2xl">📁</span>
                    <span className="font-medium text-gray-500">
                      {formData.image ? formData.image.name : 'Choose an image'}
                    </span>
                  </label>
                </div>
                {imagePreview && (
                  <div className="mt-4 rounded-lg overflow-hidden">
                    <img src={imagePreview} alt="Preview" className="w-full max-h-72 object-cover rounded-lg" />
                  </div>
                )}
              </div>

              <button 
                type="submit" 
                className="w-full py-3.5 px-8 rounded-lg text-base font-semibold cursor-pointer transition-all duration-300 inline-flex items-center justify-center gap-2 bg-gradient-primary text-white hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none"
                disabled={submitting}
              >
                {submitting ? 'Submitting...' : 'Submit Report'}
              </button>
            </form>
          )}
        </div>

        {/* Recent Tickets Card */}
        <div className="bg-white rounded-2xl p-8 shadow-xl">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">📋 Recent Tickets</h2>
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading tickets...</div>
          ) : tickets.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No tickets found. Create your first report!</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tickets.map((ticket) => (
                <div 
                  key={ticket.id} 
                  className="bg-gray-50 border border-gray-200 rounded-lg p-4 transition-all duration-300 hover:shadow-md hover:-translate-y-0.5"
                >
                  <div className="flex justify-between items-start mb-3">
                    <span className="font-bold text-[#6C5CE7] text-sm">#{ticket.id}</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${getPriorityClasses(ticket.priority)}`}>
                      {ticket.priority}
                    </span>
                  </div>
                  <div className="mb-2 text-gray-700">
                    <strong>👤 Student:</strong> {ticket.student_name}
                  </div>
                  <div className="mb-2 text-gray-700">
                    <strong>📍 Location:</strong> {ticket.location}
                  </div>
                  <div className="mb-2 text-gray-700">
                    <strong>🔧 Issue:</strong> {ticket.issue_type}
                  </div>
                  <div className="mb-2 text-gray-700">
                    <strong>📅 Created:</strong> {formatDate(ticket.created_at)}
                  </div>
                  <div className="bg-white p-3 rounded-md mt-3 text-sm text-gray-500 leading-relaxed">
                    <strong className="text-gray-700">Description:</strong>
                    <br />
                    {ticket.description}
                  </div>
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold uppercase mt-2 ${getStatusClasses(ticket.status)}`}>
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
