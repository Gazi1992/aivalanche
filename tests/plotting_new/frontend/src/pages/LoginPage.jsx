import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

const LoginPage = () => {
  const [username, setUsername] = useState('john.doe');
  const [password, setPassword] = useState('password123');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    // For now, dummy login - just navigate to sessions
    // Later this will validate credentials
    localStorage.setItem('user', JSON.stringify({ username, loginTime: new Date().toISOString() }));
    navigate('/sessions');
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <h1>Data Visualization Studio</h1>
            <p>Welcome back! Please login to continue.</p>
          </div>

          <form className="login-form" onSubmit={handleLogin}>
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g., john.doe"
                autoComplete="username"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="e.g., password123"
                autoComplete="current-password"
                required
              />
            </div>

            <button type="submit" className="login-button">
              Sign In
            </button>
          </form>

          <div className="login-footer">
            <p>New user? <a href="#">Create an account</a></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;