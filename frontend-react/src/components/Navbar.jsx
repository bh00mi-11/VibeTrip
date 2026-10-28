import React from 'react';
import { Compass, Bookmark, Mail, PlusCircle, Shield, LogOut, User as UserIcon } from 'lucide-react';

export default function Navbar({ user, currentView, onViewChange, onOpenAuth, onOpenSubmitPlace, onLogout }) {
  return (
    <header className="navbar-wrapper">
      <div className="navbar-container">
        <div className="navbar-logo" onClick={() => onViewChange('explore')}>
          <div className="navbar-logo-icon">
            <Compass size={20} strokeWidth={2.5} />
          </div>
          <span>VibeTrip</span>
        </div>

        <nav className="navbar-links">
          {user?.role === 'admin' ? (
            <>
              <button
                className={`nav-link-item ${currentView === 'admin' ? 'active' : ''}`}
                style={{ color: 'var(--primary)', fontWeight: 700 }}
                onClick={() => onViewChange('admin')}
              >
                <Shield size={16} /> Admin Console
              </button>
              <button
                className={`nav-link-item ${currentView === 'explore' ? 'active' : ''}`}
                onClick={() => onViewChange('explore')}
              >
                Explore Preview
              </button>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginLeft: '0.5rem' }}>
                <span
                  style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-main)', cursor: 'pointer' }}
                  onClick={() => onViewChange('admin')}
                >
                  {user.name} <span className="badge badge-admin">Admin</span>
                </span>
                <button className="btn btn-secondary btn-sm" onClick={onLogout}>
                  <LogOut size={14} /> Exit
                </button>
              </div>
            </>
          ) : user ? (
            <>
              <button
                className={`nav-link-item ${currentView === 'explore' ? 'active' : ''}`}
                onClick={() => onViewChange('explore')}
              >
                Explore
              </button>
              <button
                className={`nav-link-item ${currentView === 'trips' ? 'active' : ''}`}
                onClick={() => onViewChange('trips')}
              >
                <Bookmark size={16} /> Saved Trips
              </button>
              <button
                className={`nav-link-item ${currentView === 'inbox' ? 'active' : ''}`}
                onClick={() => onViewChange('inbox')}
              >
                <Mail size={16} /> Inbox
              </button>
              <button
                className={`nav-link-item ${currentView === 'contribute' ? 'active' : ''}`}
                onClick={() => onViewChange('contribute')}
              >
                {user.role === 'local' ? 'My Submissions' : 'Submissions'}
              </button>
              <button
                className="btn btn-secondary btn-sm"
                onClick={onOpenSubmitPlace}
                style={{ marginLeft: '0.3rem' }}
              >
                <PlusCircle size={15} /> Submit Spot
              </button>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginLeft: '0.6rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-main)', fontSize: '0.88rem', fontWeight: 600 }}>
                  <UserIcon size={16} className="text-muted" />
                  <span>{user.name}</span>
                  {user.role === 'local' && <span className="badge badge-local">Local</span>}
                </div>
                <button className="btn btn-secondary btn-sm" onClick={onLogout} title="Log Out">
                  <LogOut size={14} />
                </button>
              </div>
            </>
          ) : (
            <>
              <button
                className={`nav-link-item ${currentView === 'explore' ? 'active' : ''}`}
                onClick={() => onViewChange('explore')}
              >
                Explore
              </button>
              <button
                className="btn btn-outline-primary btn-sm"
                onClick={onOpenSubmitPlace}
              >
                <PlusCircle size={15} /> Submit Spot
              </button>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => onOpenAuth('login')}
              >
                Log In
              </button>
              <button
                className="btn btn-primary btn-sm"
                onClick={() => onOpenAuth('signup')}
              >
                Join VibeTrip
              </button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
