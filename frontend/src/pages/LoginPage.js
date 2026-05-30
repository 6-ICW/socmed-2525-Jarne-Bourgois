import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/home');
    } catch (err) {
      setError(err.response?.data?.error || 'Inloggen mislukt. Controleer je gegevens.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Welkom terug!</h1>
        <p className="auth-subtitle">We zijn blij je terug te zien.</p>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Gebruikersnaam</label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Voer je gebruikersnaam in"
              autoFocus
              required
            />
          </div>
          <div className="form-group">
            <label>Wachtwoord</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Voer je wachtwoord in"
              required
            />
          </div>
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? 'Inloggen...' : 'Inloggen'}
          </button>
        </form>
        <div className="auth-switch">
          Heb je nog geen account?{' '}
          <Link to="/register">Registreer</Link>
        </div>
      </div>
    </div>
  );
}
