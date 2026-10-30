import React, { useState, useEffect } from 'react';
import { Mail, Check, X, ShieldAlert, Ban, User, Phone, MapPin } from 'lucide-react';
import {
  getReceivedBuddyRequests, getSentBuddyRequests,
  acceptBuddyRequest, declineBuddyRequest, blockUser, submitReport
} from '../api';

export default function InboxView({ user }) {
  const [activeTab, setActiveTab] = useState('received');
  const [received, setReceived] = useState([]);
  const [sent, setSent] = useState([]);
  const [loading, setLoading] = useState(true);

  const role = user?.role || 'tourist';
  const roleTitle = role === 'guide'
    ? 'Guide Bookings & Traveler Requests'
    : role === 'local'
    ? 'Local Community Inquiries & Requests'
    : 'Traveler Inbox & Connections';

  const roleSubtitle = role === 'guide'
    ? 'Inquiries and booking connections from travelers requesting guided experiences and trekking tours.'
    : role === 'local'
    ? 'Travelers reaching out to discover local secret spots and authentic experiences in your area.'
    : 'Manage your travel connection requests. Contact information is strictly protected until mutual connection is accepted.';

  // Block & Report modal states
  const [actionUser, setActionUser] = useState(null); // { id, name }
  const [actionType, setActionType] = useState(''); // 'block' or 'report'
  const [reportReason, setReportReason] = useState('');
  const [reportCategory, setReportCategory] = useState('spam');

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const [rRes, sRes] = await Promise.all([
        getReceivedBuddyRequests(),
        getSentBuddyRequests(),
      ]);
      setReceived(rRes.received_requests || []);
      setSent(sRes.sent_requests || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (id) => {
    try {
      await acceptBuddyRequest(id);
      alert('Connection accepted! Contact details are now unlocked below.');
      loadRequests();
    } catch (err) {
      alert(err.message || 'Failed to accept request');
    }
  };

  const handleDecline = async (id) => {
    try {
      await declineBuddyRequest(id);
      loadRequests();
    } catch (err) {
      alert(err.message || 'Failed to decline request');
    }
  };

  const handleBlock = async () => {
    if (!actionUser) return;
    try {
      await blockUser(actionUser.id, reportReason || 'User blocked from inbox');
      alert(`User ${actionUser.name} has been blocked.`);
      setActionUser(null);
      loadRequests();
    } catch (err) {
      alert(err.message || 'Failed to block user');
    }
  };

  const handleReport = async () => {
    if (!actionUser) return;
    try {
      await submitReport(actionUser.id, reportCategory, reportReason);
      alert(`Report submitted for review by administrators.`);
      setActionUser(null);
    } catch (err) {
      alert(err.message || 'Failed to submit report');
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem' }}>{roleTitle}</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          {roleSubtitle}
        </p>
      </div>

      <div className="tab-list">
        <button
          className={`tab-item ${activeTab === 'received' ? 'active' : ''}`}
          onClick={() => setActiveTab('received')}
        >
          {role === 'guide' ? 'Received Bookings & Inquiries' : 'Received Requests'} ({received.length})
        </button>
        <button
          className={`tab-item ${activeTab === 'sent' ? 'active' : ''}`}
          onClick={() => setActiveTab('sent')}
        >
          Sent Requests ({sent.length})
        </button>
      </div>

      {loading ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
          <p style={{ color: 'var(--text-secondary)' }}>Loading your connection requests...</p>
        </div>
      ) : activeTab === 'received' ? (
        received.length === 0 ? (
          <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
            <Mail size={36} style={{ color: 'var(--text-muted)', margin: '0 auto 1rem' }} />
            <h3>No received requests yet</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
              When travelers heading to your destinations reach out to connect, their invitations will appear here.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {received.map((req) => (
              <div key={req.id} className="glass-panel" style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <h3 style={{ fontSize: '1.15rem' }}>{req.from_user_name}</h3>
                      <span className="badge" style={{ background: 'rgba(6,182,212,0.15)', color: '#22d3ee' }}>
                        For: {req.destination}
                      </span>
                      <span className={`badge ${req.status === 'accepted' ? 'badge-match' : req.status === 'declined' ? 'badge-admin' : ''}`}>
                        Status: {req.status}
                      </span>
                    </div>

                    {req.note && (
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', margin: '0.6rem 0', fontStyle: 'italic' }}>
                        "{req.note}"
                      </p>
                    )}

                    {/* Unlocked contact details on acceptance */}
                    {req.status === 'accepted' && req.revealed_contact && (
                      <div style={{
                        marginTop: '0.75rem',
                        background: 'rgba(16,185,129,0.12)',
                        border: '1px solid rgba(16,185,129,0.3)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '0.75rem 1rem',
                        fontSize: '0.85rem',
                      }}>
                        <div style={{ fontWeight: 600, color: 'var(--primary)', marginBottom: '0.2rem' }}>
                          ✓ Mutual Connection Unlocked
                        </div>
                        <div style={{ color: 'var(--text-main)' }}>
                          <strong>Contact: </strong> {req.revealed_contact}
                        </div>
                      </div>
                    )}
                  </div>

                  {req.status === 'pending' && (
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleAccept(req.id)}
                      >
                        <Check size={14} /> Accept & Share Contact
                      </button>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleDecline(req.id)}
                      >
                        <X size={14} /> Decline
                      </button>
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.5rem' }}>
                    <button
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '0.75rem' }}
                      onClick={() => {
                        setActionUser({ id: req.from_user_id, name: req.from_user_name });
                        setActionType('block');
                      }}
                    >
                      <Ban size={12} /> Block
                    </button>
                    <button
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '0.75rem' }}
                      onClick={() => {
                        setActionUser({ id: req.from_user_id, name: req.from_user_name });
                        setActionType('report');
                      }}
                    >
                      <ShieldAlert size={12} /> Report
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
        /* Sent Requests */
        sent.length === 0 ? (
          <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
            <Mail size={36} style={{ color: 'var(--text-muted)', margin: '0 auto 1rem' }} />
            <h3>No sent requests yet</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
              Explore destinations and click "Connect" on compatible traveler profiles to send invitations.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {sent.map((req) => (
              <div key={req.id} className="glass-panel" style={{ padding: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <div>
                    <div style={{ fontSize: '1rem', fontWeight: 600 }}>
                      Request to <strong>{req.to_user_name}</strong> for {req.destination}
                    </div>
                    {req.note && (
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem', marginTop: '4px' }}>
                        Note: "{req.note}"
                      </p>
                    )}
                  </div>
                  <span className={`badge ${req.status === 'accepted' ? 'badge-match' : req.status === 'declined' ? 'badge-admin' : ''}`}>
                    {req.status.toUpperCase()}
                  </span>
                </div>

                {req.status === 'accepted' && req.revealed_contact && (
                  <div style={{
                    marginTop: '0.75rem',
                    background: 'rgba(16,185,129,0.12)',
                    padding: '0.65rem 0.9rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.85rem',
                  }}>
                    <strong style={{ color: 'var(--primary)' }}>Contact Unlocked: </strong>
                    <span style={{ color: 'var(--text-main)' }}>{req.revealed_contact}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )
      )}

      {/* Safety Modal (Block or Report) */}
      {actionUser && (
        <div className="modal-overlay" onClick={() => setActionUser(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
              {actionType === 'block' ? `Block ${actionUser.name}` : `Report ${actionUser.name}`}
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              {actionType === 'block'
                ? 'Blocking this user will immediately remove them from all your traveler cards and hide all connection requests.'
                : 'Reports are confidentially sent to administrators for security and trust review.'}
            </p>

            {actionType === 'report' && (
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                  Violation Category
                </label>
                <select
                  className="input-field"
                  value={reportCategory}
                  onChange={(e) => setReportCategory(e.target.value)}
                  style={{ background: 'var(--bg-card)' }}
                >
                  <option value="spam">Spam or Commercial Promotion</option>
                  <option value="harassment">Harassment or Inappropriate Contact</option>
                  <option value="safety">Safety Concerns / Scams</option>
                  <option value="other">Other Misconduct</option>
                </select>
              </div>
            )}

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                Reason / Details
              </label>
              <textarea
                className="input-field"
                rows={3}
                placeholder="Please describe why you are reporting/blocking..."
                value={reportReason}
                onChange={(e) => setReportReason(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
              <button className="btn btn-secondary" onClick={() => setActionUser(null)}>
                Cancel
              </button>
              <button
                className={`btn ${actionType === 'block' ? 'btn-danger' : 'btn-primary'}`}
                onClick={actionType === 'block' ? handleBlock : handleReport}
              >
                {actionType === 'block' ? 'Confirm Block' : 'Submit Report'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
