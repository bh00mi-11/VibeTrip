import React, { useState, useEffect } from 'react';
import { PlusCircle, Clock, CheckCircle, XCircle, MapPin, Tag } from 'lucide-react';
import { getMySubmissions } from '../api';

export default function ContributorView({ user, onOpenSubmitModal }) {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  const role = user?.role || 'tourist';
  const roleTitle = role === 'guide' ? 'My Guide Places & Activities' : role === 'local' ? 'My Local Spots & Community Gems' : 'My Submissions';
  const roleSubtitle = role === 'guide'
    ? 'Manage your professional tour spots, trek routes, and guided experience listings'
    : role === 'local'
    ? 'Track your submitted local gems, secret viewpoints, and neighborhood spots'
    : 'Track the status of your submitted places and recommendations';
  const submitButtonText = role === 'guide' ? 'Add Guided Place' : 'Submit New Spot';

  useEffect(() => {
    loadSubmissions();
  }, []);

  const loadSubmissions = async () => {
    try {
      setLoading(true);
      const res = await getMySubmissions();
      setSubmissions(res.submissions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.75rem' }}>{roleTitle}</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            {roleSubtitle}
          </p>
        </div>
        <button className="btn btn-primary" onClick={onOpenSubmitModal}>
          <PlusCircle size={16} /> {submitButtonText}
        </button>
      </div>

      {loading ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
          <p style={{ color: 'var(--text-secondary)' }}>Loading your submissions...</p>
        </div>
      ) : submissions.length === 0 ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
          <PlusCircle size={36} style={{ color: 'var(--text-muted)', margin: '0 auto 1rem' }} />
          <h3>No submissions yet</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.5rem', marginBottom: '1.5rem' }}>
            Know a secret viewpoint, hidden trail, or cozy cafe? Share it with the VibeTrip community!
          </p>
          <button className="btn btn-primary" onClick={onOpenSubmitModal}>
            Submit Your First Spot
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {submissions.map((sub) => (
            <div key={sub.id} className="glass-panel" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <h3 style={{ fontSize: '1.2rem' }}>{sub.name}</h3>
                    <span className="badge" style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)', border: '1px solid var(--border-glass)' }}>
                      {sub.category}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '4px' }}>
                    <MapPin size={13} /> {sub.destination}
                  </div>
                </div>

                <div>
                  {sub.status === 'approved' ? (
                    <span className="badge" style={{ background: 'rgba(16,185,129,0.2)', color: '#059669' }}>
                      <CheckCircle size={12} /> Approved & Public
                    </span>
                  ) : sub.status === 'rejected' ? (
                    <span className="badge" style={{ background: 'rgba(239,68,68,0.2)', color: '#dc2626' }}>
                      <XCircle size={12} /> Rejected
                    </span>
                  ) : (
                    <span className="badge" style={{ background: 'rgba(245,158,11,0.2)', color: '#d97706' }}>
                      <Clock size={12} /> Pending Admin Review
                    </span>
                  )}
                </div>
              </div>

              {sub.description && (
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', margin: '0.75rem 0', lineHeight: 1.5 }}>
                  {sub.description}
                </p>
              )}

              {sub.review_notes && (
                <div style={{
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border-glass)',
                  padding: '0.6rem 0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.8rem',
                  color: 'var(--text-muted)',
                  marginTop: '0.5rem',
                }}>
                  <strong>Moderator feedback: </strong> {sub.review_notes}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
