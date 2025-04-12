import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export default function MicrosoftCallback() {
  const [error, setError] = useState('');
  const [isProcessing, setIsProcessing] = useState(true);
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const errorParam = urlParams.get('error');
        
        if (errorParam) {
          const errorDesc = urlParams.get('error_description') || errorParam;
          setError(`Microsoft login failed: ${errorDesc}`);
          setTimeout(() => navigate('/login'), 3000);
          return;
        }
        
        if (!code) {
          setError('');
          setTimeout(() => navigate('/login'), 3000);
          return;
        }
        
        window.history.replaceState({}, document.title, window.location.pathname);
        
        const res = await axiosInstance.post('/microsoft/callback/', { code });
        const { token, isSuperUser, userName, firstName, lastName } = res.data;
        login({ isSuperUser, userName, firstName, lastName }, token);
        navigate('/home');
      } catch (err) {
        console.error('Microsoft callback error:', err);
        const errorMessage = err.response?.data?.error || 'Microsoft login failed';
        setError(errorMessage);
        setTimeout(() => navigate('/login'), 3000);
      } finally {
        setIsProcessing(false);
      }
    };
    
    handleCallback();
  }, [navigate, login]);

  return (
    <div className="microsoft-callback-container">
      <div className="callback-box">
        <h2>Microsoft Authentication</h2>
        {error ? (
          <div className="error-message">{error}</div>
        ) : (
          <p>Completing authentication with Microsoft... Please wait.</p>
        )}
      </div>
    </div>
  );
}