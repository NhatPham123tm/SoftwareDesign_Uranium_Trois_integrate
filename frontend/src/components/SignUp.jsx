import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import './SignUp.css';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export default function Signup() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const signup = async () => {
    setError('');
    if (!firstName || !lastName || !username || !password) {
      setError('All fields are required.');
      return;
    }

    try {
      await axiosInstance.post('/signup/', { first_name: firstName, last_name: lastName, username, password });
      alert('Account created! Please log in.');
      navigate('/');
    } catch (err) {
      setError('Signup failed. Please try again.');
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-box">
        <h2>Create Account</h2>
        <p>Sign up to get started</p>

        {error && <div className="error-message">{error}</div>}
        
        <input
          value={firstName}
          onChange={e => setFirstName(e.target.value)}
          placeholder="First Name"
          className="input-field"
        />
        <input
          value={lastName}
          onChange={e => setLastName(e.target.value)}
          placeholder="Last Name"
          className="input-field"
        />
        <input
          value={username}
          onChange={e => setUsername(e.target.value)}
          placeholder="Username"
          className="input-field"
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
