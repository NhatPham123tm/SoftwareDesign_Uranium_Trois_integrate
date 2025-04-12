import { useState, useEffect } from 'react';
import { useNavigate, Link} from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/home');
    }
  }, [isAuthenticated, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (!email || !password) {
      setError('Please enter both email and password');
      setIsLoading(false);
      return;
    }

    try {
      const res = await axiosInstance.post('/login/', { email, password });
      const { token, isSuperUser, name, email: userEmail, role, status, userId } = res.data;

      // You can modify this depending on your AuthContext structure
      login({ isSuperUser, name, email: userEmail, role, status, userId }, token);

      navigate('/home');
    } catch (err) {
      const errorMessage = err.response?.data?.error || 'Login failed. Please try again.';
      setError(errorMessage);
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMicrosoftLogin = async () => {
    try {
      setIsLoading(true);
      const team = "uranium"; // or "trois-rivieres"
      const res = await axiosInstance.get(`/login/microsoft/?team=${team}`);
      window.location.href = res.data.auth_url;
    } catch (error) {
      console.error("Microsoft login failed:", error);
      setError("Failed to initiate Microsoft login. Please try again.");
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Welcome Back</h2>
        <p>Please log in to your account</p>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleLogin}>
          <input
            value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="Email"
            className="input-field"
            required
            type="email"
          />
          <input
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Password"
            type="password"
            className="input-field"
            required
          />
          <button 
            type="submit" 
            className="login-button" 
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="or-divider">
          <span>OR</span>
        </div>

        <button 
          className="microsoft-login-button"
          onClick={handleMicrosoftLogin}
          disabled={isLoading}
        >
          Login with Microsoft
        </button>
        
        <p className="signup-text">
          Don't have an account?{' '}
          <Link to="/signup" className="signup-link">Sign Up</Link>
        </p>
      </div>
    </div>
  );
}
