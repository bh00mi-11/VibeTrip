import React, { useState } from 'react';
import { X, Sparkles, AlertCircle, Lock, Mail, User, MapPin } from 'lucide-react';
import { authLogin, authSignup } from '../api';

export default function AuthModal({ initialTab = 'login', onClose, onSuccess }) {
  const [tab, setTab] = useState(initialTab);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('tourist');
  const [homeCity, setHomeCity] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (tab === 'login') {
        const res = await authLogin(email, password);
        onSuccess(res.user);
        onClose();
      } else {
        const res = await authSignup({
          email,
          password,
          name,
          role,
          home_city: homeCity,
        });
        onSuccess(res.user);
        onClose();
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const quickDemoAccounts = [
    { label: 'Demo Tourist', role: 'tourist', email: 'tourist.demo@vibetrip.com', pass: 'DemoTourist2026!', badge: 'Tourist (Mumbai)', color: '#38bdf8' },
    { label: "Rohan (Goa)", role: 'local', email: 'rohan.goa@vibetrip.com', pass: 'DemoLocal2026!', badge: 'Goa Host', color: '#10b981' },
    { label: 'Sunita (Manali)', role: 'local', email: 'sunita.manali@vibetrip.com', pass: 'DemoLocal2026!', badge: 'Manali Guide', color: '#8b5cf6' },
    { label: 'Vikram (Rishikesh)', role: 'local', email: 'vikram.rishikesh@vibetrip.com', pass: 'DemoLocal2026!', badge: 'Rishikesh Host', color: '#f59e0b' },
    { label: 'Amina (Jaipur)', role: 'local', email: 'amina.jaipur@vibetrip.com', pass: 'DemoLocal2026!', badge: 'Jaipur Storyteller', color: '#ec4899' },
    { label: 'Demo Admin', role: 'admin', email: 'admin@vibetrip.internal', pass: 'AdminSuperPass2026!', badge: 'Admin Portal', color: '#ef4444' }
  ];

  const handleInstantDemoLogin = async (acc) => {
    setEmail(acc.email);
    setPassword(acc.pass);
    setTab('login');
    setError('');
    setLoading(true);
    try {
      const res = await authLogin(acc.email, acc.pass);
      onSuccess(res.user);
      onClose();
    } catch (err) {
      setError(err.message || 'Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  const fillQuickDemo = (type) => {
    const acc = quickDemoAccounts.find(a => a.role === type) || quickDemoAccounts[0];
    setEmail(acc.email);
    setPassword(acc.pass);
    setTab('login');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h2 style={{ fontSize: '1.4rem' }}>{tab === 'login' ? 'Log In to VibeTrip' : 'Create an Account'}</h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              {tab === 'login' ? 'Access your saved trips and buddy matches' : 'Explore multi-modal vibes and join the community'}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#f87171',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-md)',
            marginBottom: '1rem',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Tab switch */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>
          <button
            type="button"
            className={`tab-item ${tab === 'login' ? 'active' : ''}`}
            onClick={() => setTab('login')}
          >
            Log In
          </button>
          <button
            type="button"
            className={`tab-item ${tab === 'signup' ? 'active' : ''}`}
            onClick={() => setTab('signup')}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
          {tab === 'signup' && (
            <>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>
                  Full Name *
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type="text"
                    required
                    className="input-field"
                    placeholder="e.g. Priya Sharma"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>
                  I want to join as *
                </label>
                <select
                  className="input-field"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  style={{ background: 'var(--bg-card)' }}
                >
                  <option value="tourist">Tourist (Discover destinations & match with buddies)</option>
                  <option value="local">Local Contributor (Share hidden gems & authentic spots)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>
                  Home City (optional)
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. Bangalore, Mumbai, Delhi"
                  value={homeCity}
                  onChange={(e) => setHomeCity(e.target.value)}
                />
              </div>
            </>
          )}

          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>
              Email Address *
            </label>
            <input
              type="email"
              required
              className="input-field"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', color: 'var(--text-secondary)' }}>
              Password *
            </label>
            <input
              type="password"
              required
              minLength={8}
              className="input-field"
              placeholder="Minimum 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '0.5rem', padding: '0.85rem' }}
            disabled={loading}
          >
            {loading ? 'Processing...' : tab === 'login' ? 'Sign In' : 'Create My Account'}
          </button>
        </form>

        {/* Quick 1-Click Demo Accounts for seamless presentation */}
        <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-glass)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <Sparkles size={14} color="#38bdf8" /> 1-Click Demo Accounts:
            </span>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Click to instant sign-in</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.45rem' }}>
            {quickDemoAccounts.map((acc) => (
              <button
                key={acc.email}
                type="button"
                disabled={loading}
                onClick={() => handleInstantDemoLogin(acc)}
                className="btn btn-secondary btn-sm"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  padding: '0.45rem 0.65rem',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'left',
                  borderLeft: `3px solid ${acc.color}`,
                  background: 'rgba(255, 255, 255, 0.03)'
                }}
              >
                <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-main)', lineHeight: 1.2 }}>
                  {acc.label}
                </span>
                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  {acc.badge}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
