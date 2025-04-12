import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import './SignUp.css';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const signup = async () => {
    setError('');
    if (!name || !email || !password) {
      setError('All fields are required.');
      return;
    }

    try {
      await axiosInstance.post('/signup/', {
        name,
        email,
        password,
        role: 2  // You can remove this line if backend assigns a default role
      });
      alert('Account created! Please log in.');
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Signup failed. Please try again.');
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-box">
        <h2>Create Account</h2>
        <p>Sign up to get started</p>

        {error && <div className="error-message">{error}</div>}

        <input
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="Full Name"
          className="input-field"
        />
        <input
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="Email"
          className="input-field"
          type="email"
        />
        <input
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="Password"
          type="password"
          className="input-field"
        />

        <button className="signup-button" onClick={signup}>Sign Up</button>

        <p className="login-text">
          Already have an account?{' '}
          <Link to="/" className="login-link">Log In</Link>
        </p>
      </div>
    </div>
  );
}
