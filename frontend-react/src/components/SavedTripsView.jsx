import React, { useState, useEffect } from 'react';
import { Bookmark, Share2, Calendar, MapPin, ChevronDown, ChevronUp } from 'lucide-react';
import { getMyTrips } from '../api';

export default function SavedTripsView({ onSelectDestination }) {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedTripId, setExpandedTripId] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await getMyTrips();
        setTrips(res.trips || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const copyShareLink = (token) => {
    const fullUrl = `${window.location.origin}/share.html?token=${token}`;
    navigator.clipboard.writeText(fullUrl);
    alert('Shareable itinerary link copied to clipboard!');
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.75rem' }}>My Saved Trips</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Your generated AI itineraries with day-by-day plans, local spots, and shareable links
        </p>
      </div>

      {loading ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
          <p style={{ color: 'var(--text-secondary)' }}>Loading your saved itineraries...</p>
        </div>
      ) : trips.length === 0 ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
          <Bookmark size={36} style={{ color: 'var(--text-muted)', margin: '0 auto 1rem' }} />
          <h3>No saved trips yet</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.5rem', marginBottom: '1.5rem' }}>
            Explore destinations, generate a 3-day itinerary, and click "Save to My Trips" to keep it here.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {trips.map((t) => {
            const isExpanded = expandedTripId === t.id;
            const days = Array.isArray(t.itinerary?.days_itinerary)
              ? t.itinerary.days_itinerary
              : (Array.isArray(t.itinerary?.days) ? t.itinerary.days : []);

            return (
              <div key={t.id} className="glass-panel" style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <h3 style={{ fontSize: '1.3rem', cursor: 'pointer', color: 'var(--text-main)' }} onClick={() => onSelectDestination(t.destination)}>
                        {t.destination}
                      </h3>
                      <span className="badge" style={{ background: 'rgba(16,185,129,0.15)', color: 'var(--primary)' }}>
                        {days.length} Days Plan
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '4px' }}>
                      <Calendar size={13} /> Saved on {t.created_at}
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => copyShareLink(t.share_token)}
                    >
                      <Share2 size={14} /> Copy Share Link
                    </button>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => setExpandedTripId(isExpanded ? null : t.id)}
                    >
                      {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      {isExpanded ? 'Hide Days' : 'View Schedule'}
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-glass)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {days.map((d, dIdx) => {
                      const dayNum = d.day_number || d.day || (dIdx + 1);
                      return (
                        <div key={dayNum} style={{ background: 'var(--bg-elevated)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)' }}>
                          <div style={{ fontWeight: 700, color: 'var(--primary)', marginBottom: '0.5rem', fontSize: '0.95rem' }}>
                            Day {dayNum}: {d.theme?.replace(/^Day \d+:\s*/, '') || d.theme || `Day ${dayNum}`}
                          </div>

                          {Array.isArray(d.slots) && d.slots.length > 0 ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.82rem' }}>
                              {d.slots.map((s, sIdx) => (
                                <div key={sIdx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.3rem', padding: '0.35rem 0', borderBottom: sIdx < d.slots.length - 1 ? '1px solid var(--border-glass)' : 'none' }}>
                                  <div>
                                    <span style={{ fontWeight: 600, color: 'var(--primary)' }}>{s.time_slot}: </span>
                                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{s.place_name} </span>
                                    {s.tip && <span style={{ color: 'var(--text-secondary)' }}>— {s.tip}</span>}
                                  </div>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                    {s.transit?.primary_mode && s.transit.primary_mode !== 'Starting Point (Hotel / Base)' && (
                                      <span style={{ fontSize: '0.72rem', background: '#e0f2fe', color: 'var(--primary)', padding: '1px 6px', borderRadius: '4px', fontWeight: 600 }}>
                                        🚗 {s.transit.primary_mode} ({s.transit.est_price_range})
                                      </span>
                                    )}
                                    {s.est_distance && (
                                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{s.est_distance}</span>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.75rem', fontSize: '0.82rem' }}>
                              <div>
                                <span style={{ color: '#d97706', fontWeight: 600 }}>Morning: </span>
                                <span style={{ color: 'var(--text-secondary)' }}>{d.morning?.title} - {d.morning?.description}</span>
                              </div>
                              <div>
                                <span style={{ color: '#0284c7', fontWeight: 600 }}>Afternoon: </span>
                                <span style={{ color: 'var(--text-secondary)' }}>{d.afternoon?.title} - {d.afternoon?.description}</span>
                              </div>
                              <div>
                                <span style={{ color: '#7c3aed', fontWeight: 600 }}>Evening: </span>
                                <span style={{ color: 'var(--text-secondary)' }}>{d.evening?.title} - {d.evening?.description}</span>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
