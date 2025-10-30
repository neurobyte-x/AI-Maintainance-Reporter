import { useState, useEffect } from 'react';
import { useNavigate, Link, useParams } from 'react-router-dom';
import { authAPI } from '../api';

function Signup({ onLogin }) {
  const navigate = useNavigate();
  const { userType } = useParams();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: userType || 'student',
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

    // Validate password length
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await authAPI.signup(formData);
      const { access_token, user } = response.data;
      onLogin(access_token, user);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>🔧 AI Maintenance Reporter</h1>
          <p>Create your account</p>
          <h2 className="user-type-title">
            {userType === 'admin' ? '👨‍💼 Admin Registration' : '👨‍🎓 Student Registration'}
          </h2>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="full_name">Full Name</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="Enter your full name"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">REVA Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your.name@reva.edu.in"
              required
            />
            <small style={{ color: '#64748b', fontSize: '0.875rem' }}>
              Only @reva.edu.in emails are allowed
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="At least 6 characters"
              required
              minLength={6}
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account?{' '}
          <Link to={`/login/${userType || 'student'}`}>
            <button>Login here</button>
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

export default Signup;
