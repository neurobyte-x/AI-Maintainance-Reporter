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
    <div className="flex justify-center items-center min-h-screen p-8 bg-gray-50">
      <div className="bg-white rounded-2xl p-12 shadow-xl w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[#6C5CE7] mb-2"> AI Maintenance Reporter</h1>
          <p className="text-gray-500">REVA University</p>
          <h2 className="text-2xl mt-4 text-gray-900 flex items-center justify-center gap-2">
            {userType === 'admin' ? '👨‍💼 Admin Login' : '👨‍🎓 Student Login'}
          </h2>
        </div>

        {error && (
          <div className="bg-red-50 text-red-800 p-3 rounded-lg mb-4 border-l-4 border-red-500">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label htmlFor="email" className="block mb-2 font-semibold text-gray-900">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your.name@reva.edu.in"
              required
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg text-base transition-colors duration-300 focus:outline-none focus:border-[#6C5CE7]"
            />
          </div>

          <div className="mb-6">
            <label htmlFor="password" className="block mb-2 font-semibold text-gray-900">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg text-base transition-colors duration-300 focus:outline-none focus:border-[#6C5CE7]"
            />
          </div>

          <button 
            type="submit" 
            className="w-full py-3.5 px-8 rounded-lg text-base font-semibold cursor-pointer transition-all duration-300 inline-flex items-center justify-center gap-2 bg-gradient-primary text-white hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none"
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="text-center mt-6 text-gray-500">
          Don't have an account?{' '}
          <Link to={`/signup/${userType || 'student'}`}>
            <button className="bg-transparent border-none text-[#6C5CE7] cursor-pointer font-semibold underline">
              Sign up here
            </button>
          </Link>
        </div>
        <div className="text-center mt-6">
          <Link to="/">
            <button className="w-full mt-2 py-3 px-4 bg-gray-100 text-gray-900 border border-gray-200 rounded-lg font-semibold cursor-pointer transition-all duration-300 hover:bg-gray-200">
              ← Back to Home
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
