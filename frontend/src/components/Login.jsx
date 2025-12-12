import { useState, useEffect } from 'react';
import { useNavigate, Link, useParams } from 'react-router-dom';
import { authAPI } from '../api';

function Login({ onLogin }) {
  const navigate = useNavigate();
  const { userType } = useParams();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate email domain
    if (!formData.email.endsWith('@reva.edu.in')) {
      setError('Only @reva.edu.in emails are allowed');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login(formData);
      const { access_token, user } = response.data;
      
      if (userType === 'admin' && user.role !== 'admin') {
        setError('You do not have admin privileges');
        return;
      }
      
      if (userType === 'student' && user.role === 'admin') {
        setError('Please use admin login');
        return;
      }
      
      onLogin(access_token, user);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1> AI Maintenance Reporter</h1>
          <p>REVA University</p>
          <h2 className="user-type-title">
            {userType === 'admin' ? '👨‍💼 Admin Login' : '👨‍🎓 Student Login'}
          </h2>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your.name@reva.edu.in"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="auth-footer">
          Don't have an account?{' '}
          <Link to={`/signup/${userType || 'student'}`}>
            <button>Sign up here</button>
          </Link>
        </div>
        <div className="auth-footer">
          <Link to="/">
            <button className="back-btn">← Back to Home</button>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
