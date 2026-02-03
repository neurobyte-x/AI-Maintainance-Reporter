import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ticketsAPI } from '../api';

function AdminDashboard({ user, onLogout }) {
  const navigate = useNavigate();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

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
    if (filter === 'resolved') {
      return ticket.status === 'resolved' || ticket.status === 'closed';
    }
    return ticket.status === filter;
  });

  const stats = {
    total: tickets.length,
    pending: tickets.filter(t => t.status === 'pending').length,
    inProgress: tickets.filter(t => t.status === 'in_progress').length,
    resolved: tickets.filter(t => t.status === 'resolved' || t.status === 'closed').length,
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen text-2xl text-[#6C5CE7]">
        Loading tickets...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-gradient-primary text-white p-8 shadow-lg">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2"> Admin Dashboard</h1>
            <p className="opacity-90 text-lg">Welcome, {user?.full_name}</p>
          </div>
          <button 
            onClick={onLogout} 
            className="px-6 py-3 bg-white/20 backdrop-blur-sm border border-white/30 text-white rounded-lg font-semibold transition-all duration-300 hover:bg-white/30 hover:-translate-y-0.5"
          >
            Logout
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-lg flex items-center gap-4 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
            <div className="text-4xl w-15 h-15 flex items-center justify-center rounded-xl bg-gradient-primary">📊</div>
            <div>
              <div className="text-4xl font-extrabold text-gray-900">{stats.total}</div>
              <div className="text-sm text-gray-500 font-medium">Total Tickets</div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg flex items-center gap-4 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
            <div className="text-4xl w-15 h-15 flex items-center justify-center rounded-xl bg-gradient-warning">⏳</div>
            <div>
              <div className="text-4xl font-extrabold text-gray-900">{stats.pending}</div>
              <div className="text-sm text-gray-500 font-medium">Pending</div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg flex items-center gap-4 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
            <div className="text-4xl w-15 h-15 flex items-center justify-center rounded-xl bg-gradient-primary">🔄</div>
            <div>
              <div className="text-4xl font-extrabold text-gray-900">{stats.inProgress}</div>
              <div className="text-sm text-gray-500 font-medium">In Progress</div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg flex items-center gap-4 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">
            <div className="text-4xl w-15 h-15 flex items-center justify-center rounded-xl bg-gradient-success">✅</div>
            <div>
              <div className="text-4xl font-extrabold text-gray-900">{stats.resolved}</div>
              <div className="text-sm text-gray-500 font-medium">Resolved</div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-8 flex-wrap">
          {[
            { key: 'all', label: `All (${tickets.length})` },
            { key: 'pending', label: `Pending (${stats.pending})` },
            { key: 'in_progress', label: `In Progress (${stats.inProgress})` },
            { key: 'resolved', label: `Resolved (${stats.resolved})` },
          ].map((btn) => (
            <button
              key={btn.key}
              className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
                filter === btn.key
                  ? 'bg-gradient-primary text-white border-transparent'
                  : 'bg-white border-2 border-gray-200 text-gray-500 hover:border-[#6C5CE7] hover:text-[#6C5CE7]'
              }`}
              onClick={() => setFilter(btn.key)}
            >
              {btn.label}
            </button>
          ))}
        </div>

        {/* Tickets Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTickets.length === 0 ? (
            <div className="col-span-full text-center py-16 bg-white rounded-xl text-gray-400 text-lg">
              <p>No tickets found in this category</p>
            </div>
          ) : (
            filteredTickets.map((ticket) => (
              <div 
                key={ticket.id} 
                className="bg-white rounded-xl p-6 shadow-lg transition-all duration-300 border-2 border-transparent hover:-translate-y-1 hover:shadow-xl hover:border-[#6C5CE7]"
              >
                <div className="flex justify-between items-center mb-4 pb-4 border-b-2 border-gray-100">
                  <div className="font-bold text-lg text-gray-900">Ticket #{ticket.id}</div>
                  <div className="flex gap-2">
                    <span 
                      className="px-3 py-1 rounded-md text-xs font-bold text-white uppercase tracking-wide"
                      style={{ backgroundColor: getPriorityColor(ticket?.priority ?? 'unknown') }}
                    >
                      {(ticket?.priority ?? 'unknown').toUpperCase()}
                    </span>
                    <span 
                      className="px-3 py-1 rounded-md text-xs font-bold text-white uppercase tracking-wide"
                      style={{ backgroundColor: getStatusColor(ticket?.status ?? 'unknown') }}
                    >
                      {(ticket?.status ?? 'unknown').replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                </div>

                <div className="mb-4">
                  {[
                    { label: 'Student:', value: ticket.student_name },
                    { label: 'Location:', value: ticket.location },
                    { label: 'Issue Type:', value: ticket.issue_type },
                    { label: 'Date:', value: new Date(ticket.created_at).toLocaleString() },
                  ].map((info, index) => (
                    <div key={index} className="flex justify-between py-2 border-b border-gray-100">
                      <span className="font-semibold text-gray-500 text-sm">{info.label}</span>
                      <span className="text-gray-900 font-medium text-right">{info.value}</span>
                    </div>
                  ))}
                </div>

                <div className="my-4 p-4 bg-gray-50 rounded-lg border-l-4 border-[#6C5CE7]">
                  <strong className="block mb-2 text-gray-900">Description:</strong>
                  <p className="text-gray-600 leading-relaxed text-sm">{ticket.description}</p>
                </div>

                <div className="flex gap-2 mt-4">
                  {ticket.status === 'pending' && (
                    <button
                      className="flex-1 py-3 px-4 rounded-lg font-semibold text-white transition-all duration-300 bg-gradient-primary hover:-translate-y-0.5 hover:shadow-lg"
                      onClick={() => handleStatusUpdate(ticket.id, 'in_progress')}
                    >
                      ⚙️ Start Working
                    </button>
                  )}
                  {ticket.status === 'in_progress' && (
                    <button
                      className="flex-1 py-3 px-4 rounded-lg font-semibold text-white transition-all duration-300 bg-gradient-success hover:-translate-y-0.5 hover:shadow-lg"
                      onClick={() => handleStatusUpdate(ticket.id, 'resolved')}
                    >
                      ✅ Mark Resolved
                    </button>
                  )}
                  {(ticket.status === 'resolved' || ticket.status === 'closed') && (
                    <span className="flex-1 py-3 px-4 rounded-lg font-semibold text-teal-700 bg-emerald-100 text-center tracking-wide">
                      ✅ Completed
                    </span>
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
