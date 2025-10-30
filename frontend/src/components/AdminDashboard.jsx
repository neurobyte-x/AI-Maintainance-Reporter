import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ticketsAPI } from '../api';
import './AdminDashboard.css';

function AdminDashboard({ user, onLogout }) {
  const navigate = useNavigate();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedTicket, setSelectedTicket] = useState(null);

  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/');
      return;
    }
    fetchTickets();
  }, [user, navigate]);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const response = await ticketsAPI.getAllTickets();
      console.log('Fetched tickets:', response.data);
      console.log('Stats - Resolved:', response.data.filter(t => t.status === 'resolved').length);
      setTickets(response.data);
    } catch (error) {
      console.error('Error fetching tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (ticketId, newStatus) => {
    try {
      console.log(`Updating ticket ${ticketId} to status: ${newStatus}`);
      const response = await ticketsAPI.updateStatus(ticketId, newStatus);
      console.log('Update response:', response);
      await fetchTickets();
      console.log('Tickets refetched');
      setSelectedTicket(null);
    } catch (error) {
      console.error('Error updating ticket:', error);
      alert('Failed to update ticket status');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return '#f59e0b';
      case 'in_progress': return '#3b82f6';
      case 'resolved': return '#10b981';
      case 'closed': return '#6b7280';
      default: return '#94a3b8';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#94a3b8';
    }
  };

  const filteredTickets = tickets.filter(ticket => {
    if (filter === 'all') return true;
    return ticket.status === filter;
  });

  const stats = {
    total: tickets.length,
    pending: tickets.filter(t => t.status === 'pending').length,
    inProgress: tickets.filter(t => t.status === 'in_progress').length,
    resolved: tickets.filter(t => t.status === 'resolved').length,
  };

  if (loading) {
    return <div className="loading-container">Loading tickets...</div>;
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <div className="header-content">
          <div className="header-left">
            <h1>🔧 Admin Dashboard</h1>
            <p>Welcome, {user?.full_name}</p>
          </div>
          <button onClick={onLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <div className="dashboard-container">
        <div className="stats-grid">
          <div className="stat-card total">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-value">{stats.total}</div>
              <div className="stat-label">Total Tickets</div>
            </div>
          </div>
          <div className="stat-card pending">
            <div className="stat-icon">⏳</div>
            <div className="stat-content">
              <div className="stat-value">{stats.pending}</div>
              <div className="stat-label">Pending</div>
            </div>
          </div>
          <div className="stat-card in-progress">
            <div className="stat-icon">🔄</div>
            <div className="stat-content">
              <div className="stat-value">{stats.inProgress}</div>
              <div className="stat-label">In Progress</div>
            </div>
          </div>
          <div className="stat-card resolved">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-value">{stats.resolved}</div>
              <div className="stat-label">Resolved</div>
            </div>
          </div>
        </div>

        <div className="filters">
          <button 
            className={filter === 'all' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilter('all')}
          >
            All ({tickets.length})
          </button>
          <button 
            className={filter === 'pending' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilter('pending')}
          >
            Pending ({stats.pending})
          </button>
          <button 
            className={filter === 'in_progress' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilter('in_progress')}
          >
            In Progress ({stats.inProgress})
          </button>
          <button 
            className={filter === 'resolved' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilter('resolved')}
          >
            Resolved ({stats.resolved})
          </button>
        </div>

        <div className="tickets-grid">
          {filteredTickets.length === 0 ? (
            <div className="no-tickets">
              <p>No tickets found in this category</p>
            </div>
          ) : (
            filteredTickets.map((ticket) => (
              <div key={ticket.id} className="admin-ticket-card">
                <div className="ticket-header">
                  <div className="ticket-id">Ticket #{ticket.id}</div>
                  <div className="ticket-badges">
                    <span 
                      className="priority-badge"
                      style={{ backgroundColor: getPriorityColor(ticket.priority) }}
                    >
                      {ticket.priority.toUpperCase()}
                    </span>
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(ticket.status) }}
                    >
                      {ticket.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                </div>

                <div className="ticket-info">
                  <div className="info-row">
                    <span className="info-label">Student:</span>
                    <span className="info-value">{ticket.student_name}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Location:</span>
                    <span className="info-value">{ticket.location}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Issue Type:</span>
                    <span className="info-value">{ticket.issue_type}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Date:</span>
                    <span className="info-value">
                      {new Date(ticket.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                <div className="ticket-description">
                  <strong>Description:</strong>
                  <p>{ticket.description}</p>
                </div>

                <div className="ticket-actions">
                  {ticket.status === 'pending' && (
                    <button
                      className="action-btn btn-progress"
                      onClick={() => handleStatusUpdate(ticket.id, 'in_progress')}
                    >
                      Start Working
                    </button>
                  )}
                  {ticket.status === 'in_progress' && (
                    <button
                      className="action-btn btn-resolve"
                      onClick={() => handleStatusUpdate(ticket.id, 'resolved')}
                    >
                      Mark Resolved
                    </button>
                  )}
                  {ticket.status === 'resolved' && (
                    <button
                      className="action-btn btn-close"
                      onClick={() => handleStatusUpdate(ticket.id, 'closed')}
                    >
                      Close Ticket
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;
