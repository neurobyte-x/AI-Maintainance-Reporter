import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

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
    <div className="font-sans text-gray-800 overflow-x-hidden">
      {/* Navbar */}
      <nav className="bg-white/95 backdrop-blur-sm fixed top-0 left-0 right-0 z-50 shadow-md">
        <div className="max-w-6xl mx-auto px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2 text-2xl font-bold text-[#6C5CE7]">
            <span className="text-3xl">🔧</span>
            <span>AI Maintenance Reporter</span>
          </div>
          <div className="hidden md:flex gap-8">
            <a href="#features" className="text-gray-600 font-medium hover:text-[#6C5CE7] transition-colors">Features</a>
            <a href="#how-it-works" className="text-gray-600 font-medium hover:text-[#6C5CE7] transition-colors">How It Works</a>
            <a href="#about" className="text-gray-600 font-medium hover:text-[#6C5CE7] transition-colors">About</a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-8 max-w-6xl mx-auto grid md:grid-cols-2 gap-16 items-center min-h-[90vh]">
        <div className="animate-fadeInUp">
          <h1 className="text-4xl md:text-5xl font-extrabold leading-tight mb-6 text-gray-900">
            Smart Maintenance <span className="text-gradient">Reporting System</span>
          </h1>
          <p className="text-xl text-gray-500 mb-10 leading-relaxed">
            AI-powered solution for campus maintenance. Report issues instantly with image recognition and automated ticket generation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <button 
              className="px-8 py-4 text-lg font-semibold rounded-xl cursor-pointer transition-all duration-300 flex items-center justify-center gap-2 bg-gradient-primary text-white shadow-lg shadow-[#6C5CE7]/40 hover:-translate-y-1 hover:shadow-xl hover:shadow-[#6C5CE7]/50"
              onClick={() => handleLoginChoice('student')}
            >
              <span className="text-2xl">👨‍🎓</span>
              Student Login
            </button>
            <button 
              className="px-8 py-4 text-lg font-semibold rounded-xl cursor-pointer transition-all duration-300 flex items-center justify-center gap-2 bg-white text-[#6C5CE7] border-2 border-[#6C5CE7] hover:bg-[#6C5CE7] hover:text-white hover:-translate-y-1"
              onClick={() => handleLoginChoice('admin')}
            >
              <span className="text-2xl">👨‍💼</span>
              Admin Login
            </button>
          </div>
          <p className="text-gray-400 flex items-center gap-2">
            <span className="text-xl">ℹ️</span>
            Exclusively for @reva.edu.in email addresses
          </p>
        </div>
        <div className="relative h-[500px] hidden md:block">
          <div className="absolute top-12 left-12 bg-white p-6 rounded-2xl shadow-xl flex items-center gap-4 animate-float">
            <div className="text-4xl">🤖</div>
            <div className="font-semibold text-gray-900">AI-Powered Analysis</div>
          </div>
          <div className="absolute top-48 right-12 bg-white p-6 rounded-2xl shadow-xl flex items-center gap-4 animate-float-delay-1">
            <div className="text-4xl">📸</div>
            <div className="font-semibold text-gray-900">Image Recognition</div>
          </div>
          <div className="absolute bottom-24 left-24 bg-white p-6 rounded-2xl shadow-xl flex items-center gap-4 animate-float-delay-2">
            <div className="text-4xl">⚡</div>
            <div className="font-semibold text-gray-900">Instant Tickets</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-8 bg-gradient-to-b from-gray-50 to-white">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-extrabold text-gray-900 mb-4">Powerful Features</h2>
          <p className="text-xl text-gray-500">Everything you need for efficient maintenance management</p>
        </div>
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            { icon: '🎯', title: 'Smart Detection', desc: 'AI automatically identifies and classifies maintenance issues from images' },
            { icon: '📊', title: 'Priority Assignment', desc: 'Intelligent priority levels based on issue severity and urgency' },
            { icon: '🔔', title: 'Real-time Updates', desc: 'Get instant notifications on ticket status and resolution progress' },
            { icon: '📱', title: 'Easy Submission', desc: 'Simple interface to report issues with just a photo and location' },
            { icon: '🛠️', title: 'Admin Dashboard', desc: 'Comprehensive tools for tracking and managing all maintenance tickets' },
            { icon: '📈', title: 'Analytics', desc: 'Track trends and performance metrics for campus maintenance' },
          ].map((feature, index) => (
            <div key={index} className="bg-white p-8 rounded-2xl shadow-lg hover:-translate-y-2 hover:shadow-2xl transition-all duration-300 cursor-pointer">
              <div className="text-5xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-gray-500 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 px-8 bg-white">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-extrabold text-gray-900 mb-4">How It Works</h2>
          <p className="text-xl text-gray-500">Simple 3-step process to report and resolve issues</p>
        </div>
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-center gap-8">
          {[
            { num: '1', title: 'Take a Photo', desc: 'Capture an image of the maintenance issue you want to report' },
            { num: '2', title: 'AI Analysis', desc: 'Our AI analyzes the image and automatically generates a detailed ticket' },
            { num: '3', title: 'Get It Fixed', desc: 'Admin team receives the ticket and resolves the issue promptly' },
          ].map((step, index) => (
            <div key={index} className="flex items-center gap-8">
              <div className="flex-1 text-center p-8">
                <div className="w-20 h-20 bg-gradient-primary text-white rounded-full flex items-center justify-center text-3xl font-bold mx-auto mb-6 shadow-lg shadow-[#6C5CE7]/30">
                  {step.num}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{step.title}</h3>
                <p className="text-gray-500 leading-relaxed">{step.desc}</p>
              </div>
              {index < 2 && <div className="text-3xl text-[#6C5CE7] font-bold hidden md:block">→</div>}
            </div>
          ))}
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 px-8 bg-[#F4EEFF]">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-4xl font-extrabold text-gray-900 mb-6">About Our System</h2>
            <p className="text-lg text-gray-600 leading-relaxed mb-6">
              The AI Maintenance Reporter is a cutting-edge solution designed specifically for REVA University campus. 
              Using advanced artificial intelligence powered by Google's Gemini 2.5 Pro, we analyze maintenance issues 
              in real-time and create actionable tickets automatically.
            </p>
            <p className="text-lg text-gray-600 leading-relaxed mb-6">
              Our system specializes in detecting issues with fans, lights, furniture, electronics, and electrical 
              components, ensuring a safe and functional campus environment for everyone.
            </p>
            <div className="grid grid-cols-3 gap-8 mt-12">
              {[
                { value: 'AI', label: 'Powered' },
                { value: '24/7', label: 'Available' },
                { value: 'Fast', label: 'Resolution' },
              ].map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-4xl font-extrabold text-gray-900 mb-2">{stat.value}</div>
                  <div className="text-gray-600">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {['React', 'FastAPI', 'Gemini AI', 'LangGraph'].map((tech, index) => (
              <div key={index} className="bg-white p-6 rounded-xl text-center font-semibold text-lg border border-gray-200 text-gray-900">
                {tech}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12 px-8">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12 mb-8">
          <div>
            <h4 className="text-xl font-bold mb-4">AI Maintenance Reporter</h4>
            <p className="text-gray-400 leading-relaxed">Making campus maintenance smarter and faster</p>
          </div>
          <div>
            <h4 className="text-xl font-bold mb-4">Quick Links</h4>
            <a href="#features" className="block text-gray-400 hover:text-[#6C5CE7] mb-2 transition-colors">Features</a>
            <a href="#how-it-works" className="block text-gray-400 hover:text-[#6C5CE7] mb-2 transition-colors">How It Works</a>
            <a href="#about" className="block text-gray-400 hover:text-[#6C5CE7] mb-2 transition-colors">About</a>
          </div>
          <div>
            <h4 className="text-xl font-bold mb-4">Contact</h4>
            <p className="text-gray-400 leading-relaxed">REVA University</p>
            <p className="text-gray-400 leading-relaxed">support@reva.edu.in</p>
          </div>
        </div>
        <div className="text-center pt-8 border-t border-gray-700 text-gray-400">
          <p>&copy; 2025 AI Maintenance Reporter. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
