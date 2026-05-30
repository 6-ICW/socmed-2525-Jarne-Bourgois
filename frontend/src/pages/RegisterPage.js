import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password !== confirm) { setError('Wachtwoorden komen niet overeen.'); return; }
    if (username.trim().length < 2) { setError('Gebruikersnaam moet minstens 2 tekens bevatten.'); return; }
    setLoading(true);
    try {
      await register(username.trim(), password);
      navigate('/home');
    } catch (err) {
      const data = err.response?.data;
      const msg = data?.username?.[0] || data?.password?.[0] || data?.error || 'Registratie mislukt.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Account aanmaken</h1>
        <p className="auth-subtitle">Begin je avontuur!</p>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Gebruikersnaam</label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Kies een gebruikersnaam"
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
              placeholder="Kies een wachtwoord"
              required
            />
          </div>
          <div className="form-group">
            <label>Bevestig wachtwoord</label>
            <input
              type="password"
              value={confirm}
              onChange={e => setConfirm(e.target.value)}
              placeholder="Herhaal je wachtwoord"
              required
            />
          </div>
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? 'Account aanmaken...' : 'Registreren'}
          </button>
        </form>
        <div className="auth-switch">
          Al een account?{' '}
          <Link to="/login">Inloggen</Link>
        </div>
      </div>
    </div>
  );
}
