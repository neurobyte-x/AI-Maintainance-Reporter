import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

function LandingPage() {
  const navigate = useNavigate();
  const [loginType, setLoginType] = useState(null);

  useEffect(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }, []);

  const handleLoginChoice = (type) => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setLoginType(type);
    navigate(`/login/${type}`);
  };

  return (
    <div className="landing-page">
      <nav className="navbar">
        <div className="nav-container">
          <div className="logo">
            <span className="logo-icon"></span>
            <span className="logo-text">AI Maintenance Reporter</span>
          </div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#about">About</a>
          </div>
        </div>
      </nav>

      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Smart Maintenance <span className="highlight">Reporting System</span>
          </h1>
          <p className="hero-subtitle">
            AI-powered solution for campus maintenance. Report issues instantly with image recognition and automated ticket generation.
          </p>
          <div className="cta-buttons">
            <button className="btn btn-primary" onClick={() => handleLoginChoice('student')}>
              <span className="btn-icon">👨‍🎓</span>
              Student Login
            </button>
            <button className="btn btn-secondary" onClick={() => handleLoginChoice('admin')}>
              <span className="btn-icon">👨‍💼</span>
              Admin Login
            </button>
          </div>
          <p className="hero-note">
            <span className="info-icon">ℹ️</span>
            Exclusively for @reva.edu.in email addresses
          </p>
        </div>
        <div className="hero-image">
          <div className="floating-card card-1">
            <div className="card-icon">🤖</div>
            <div className="card-text">AI-Powered Analysis</div>
          </div>
          <div className="floating-card card-2">
            <div className="card-icon">📸</div>
            <div className="card-text">Image Recognition</div>
          </div>
          <div className="floating-card card-3">
            <div className="card-icon">⚡</div>
            <div className="card-text">Instant Tickets</div>
          </div>
        </div>
      </section>

      <section id="features" className="features">
        <div className="section-header">
          <h2>Powerful Features</h2>
          <p>Everything you need for efficient maintenance management</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Smart Detection</h3>
            <p>AI automatically identifies and classifies maintenance issues from images</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Priority Assignment</h3>
            <p>Intelligent priority levels based on issue severity and urgency</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔔</div>
            <h3>Real-time Updates</h3>
            <p>Get instant notifications on ticket status and resolution progress</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📱</div>
            <h3>Easy Submission</h3>
            <p>Simple interface to report issues with just a photo and location</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🛠️</div>
            <h3>Admin Dashboard</h3>
            <p>Comprehensive tools for tracking and managing all maintenance tickets</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📈</div>
            <h3>Analytics</h3>
            <p>Track trends and performance metrics for campus maintenance</p>
          </div>
        </div>
      </section>

      <section id="how-it-works" className="how-it-works">
        <div className="section-header">
          <h2>How It Works</h2>
          <p>Simple 3-step process to report and resolve issues</p>
        </div>
        <div className="steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Take a Photo</h3>
              <p>Capture an image of the maintenance issue you want to report</p>
            </div>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>AI Analysis</h3>
              <p>Our AI analyzes the image and automatically generates a detailed ticket</p>
            </div>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Get It Fixed</h3>
              <p>Admin team receives the ticket and resolves the issue promptly</p>
            </div>
          </div>
        </div>
      </section>

      <section id="about" className="about">
        <div className="about-content">
          <div className="about-text">
            <h2>About Our System</h2>
            <p>
              The AI Maintenance Reporter is a cutting-edge solution designed specifically for REVA University campus. 
              Using advanced artificial intelligence powered by Google's Gemini 2.5 Pro, we analyze maintenance issues 
              in real-time and create actionable tickets automatically.
            </p>
            <p>
              Our system specializes in detecting issues with fans, lights, furniture, electronics, and electrical 
              components, ensuring a safe and functional campus environment for everyone.
            </p>
            <div className="stats">
              <div className="stat">
                <div className="stat-number">AI</div>
                <div className="stat-label">Powered</div>
              </div>
              <div className="stat">
                <div className="stat-number">24/7</div>
                <div className="stat-label">Available</div>
              </div>
              <div className="stat">
                <div className="stat-number">Fast</div>
                <div className="stat-label">Resolution</div>
              </div>
            </div>
          </div>
          <div className="about-image">
            <div className="tech-stack">
              <div className="tech-item">React</div>
              <div className="tech-item">FastAPI</div>
              <div className="tech-item">Gemini AI</div>
              <div className="tech-item">LangGraph</div>
            </div>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>AI Maintenance Reporter</h4>
            <p>Making campus maintenance smarter and faster</p>
          </div>
          <div className="footer-section">
            <h4>Quick Links</h4>
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#about">About</a>
          </div>
          <div className="footer-section">
            <h4>Contact</h4>
            <p>REVA University</p>
            <p>support@reva.edu.in</p>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 AI Maintenance Reporter. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
