import React, { useState } from 'react';
import { X, PlusCircle, CheckCircle, AlertCircle } from 'lucide-react';
import { submitContributePlace } from '../api';

export default function SubmitPlaceModal({ onClose, onSuccess }) {
  const [destination, setDestination] = useState('');
  const [category, setCategory] = useState('viewpoint');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [address, setAddress] = useState('');
  const [contactInfo, setContactInfo] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await submitContributePlace({
        destination,
        category,
        name,
        description,
        address,
        contact_info: contactInfo,
      });
      setSuccess(true);
      setTimeout(() => {
        if (onSuccess) onSuccess();
        onClose();
      }, 1500);
    } catch (err) {
      setError(err.message || 'Failed to submit place. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h2 style={{ fontSize: '1.35rem' }}>Submit a Local Gem or Query</h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Recommend scenic viewpoints, authentic cafes, heritage food, or local activities.
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {success ? (
          <div style={{ padding: '2rem 1rem', textAlign: 'center' }}>
            <CheckCircle size={40} style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
            <h3>Submission Sent for Review!</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginTop: '0.5rem' }}>
              Thank you for contributing! Your spot has entered the moderation queue and will appear publicly once approved.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
            {error && (
              <div style={{ background: 'rgba(239,68,68,0.15)', color: '#f87171', padding: '0.75rem', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem' }}>
                {error}
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                  Destination *
                </label>
                <input
                  type="text"
                  required
                  className="input-field"
                  placeholder="e.g. Shillong, Manali"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                  Category *
                </label>
                <select
                  className="input-field"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  style={{ background: 'var(--bg-card)' }}
                >
                  <option value="viewpoint">Scenic Viewpoint</option>
                  <option value="cafe">Cafe / Coffee</option>
                  <option value="food">Local Food / Restaurant</option>
                  <option value="attraction">Hidden Attraction</option>
                  <option value="activity">Adventure / Activity</option>
                  <option value="query">Traveler Question / Query</option>
                </select>
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                Place / Spot Name *
              </label>
              <input
                type="text"
                required
                className="input-field"
                placeholder="e.g. Laitlum Canyon Sunset Edge"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                Description & Insider Tips *
              </label>
              <textarea
                required
                rows={3}
                className="input-field"
                placeholder="What makes this place special? Best time of day, vibe, peacefulness level..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                  Address / Landmark
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Near Police Bazar"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                  Contact (optional)
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Instagram or phone"
                  value={contactInfo}
                  onChange={(e) => setContactInfo(e.target.value)}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Submitting...' : 'Send for Review'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
