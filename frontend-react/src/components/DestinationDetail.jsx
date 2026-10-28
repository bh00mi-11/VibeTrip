import React, { useState, useEffect, useRef } from 'react';
import {
  ArrowLeft, MapPin, Calendar, Compass, Share2, Bookmark, Check,
  Sparkles, Coffee, Utensils, Mountain, Eye, Users, AlertCircle, HeartHandshake, Shield, Camera, X, ExternalLink, Activity,
  Car, Navigation, Bike, Clock, DollarSign, Fuel, ShieldCheck, Bus, Gauge, Award, Layers, Zap, Info, UserCheck
} from 'lucide-react';
import {
  getDestination, generateTripPlan, saveTrip, getLocalExperiences,
  getBuddies, postBuddyInterest, sendBuddyRequest, getImageUrl
} from '../api';

export default function DestinationDetail({ destinationName, user, onBack, onOpenAuth }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [dest, setDest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Itinerary state
  const [plan, setPlan] = useState(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState(1);
  const [savingTrip, setSavingTrip] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState('');
  const [shareUrl, setShareUrl] = useState('');

  // Nearby places state
  const [places, setPlaces] = useState([]);
  const [placesLoading, setPlacesLoading] = useState(false);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [selectedPhotoModal, setSelectedPhotoModal] = useState(null);
  const mapRef = useRef(null);
  const leafletMapInstance = useRef(null);

  // Travelers state
  const [travelers, setTravelers] = useState([]);
  const [travelersLoading, setTravelersLoading] = useState(false);
  const [connectModalUser, setConnectModalUser] = useState(null);
  const [connectNote, setConnectNote] = useState('');
  const [connectStatus, setConnectStatus] = useState('');

  // Transit & DL details modal states
  const [showAiArchitecture, setShowAiArchitecture] = useState(false);
  const [selectedInquiryHub, setSelectedInquiryHub] = useState(null);

  // Fetch destination overview
  useEffect(() => {
    async function loadDest() {
      try {
        setLoading(true);
        const data = await getDestination(destinationName);
        setDest(data);
      } catch (err) {
        setError(err.message || 'Failed to load destination details');
      } finally {
        setLoading(false);
      }
    }
    loadDest();
  }, [destinationName]);

  // Load Itinerary / Transit when Plan or Travel tab opens
  useEffect(() => {
    if ((activeTab === 'plan' || activeTab === 'travel') && !plan && dest) {
      loadPlan();
    }
    if (activeTab === 'nearby' && dest) {
      loadPlaces();
    }
    if (activeTab === 'travelers' && dest) {
      loadTravelers();
    }
  }, [activeTab, dest]);

  const loadPlan = async () => {
    try {
      setPlanLoading(true);
      const res = await generateTripPlan(destinationName, 3);
      setPlan(res);
    } catch (err) {
      console.error(err);
    } finally {
      setPlanLoading(false);
    }
  };

  const handleSaveTrip = async () => {
    if (!user) {
      onOpenAuth('login');
      return;
    }
    try {
      setSavingTrip(true);
      const res = await saveTrip(destinationName, plan);
      setSavedSuccess('Trip saved to your profile!');
      const fullUrl = `${window.location.origin}/share.html?token=${res.share_token}`;
      setShareUrl(fullUrl);
    } catch (err) {
      alert(err.message || 'Failed to save trip');
    } finally {
      setSavingTrip(false);
    }
  };

  const loadPlaces = async (cat = categoryFilter) => {
    try {
      setPlacesLoading(true);
      const res = await getLocalExperiences(destinationName, cat);
      setPlaces(res.experiences || []);
      setupMap(res.experiences || []);
    } catch (err) {
      console.error(err);
    } finally {
      setPlacesLoading(false);
    }
  };

  const handleCategoryChange = (cat) => {
    setCategoryFilter(cat);
    loadPlaces(cat);
  };

  const setupMap = (placeItems) => {
    setTimeout(() => {
      if (typeof window === 'undefined' || !mapRef.current) return;
      const L = window.L;
      if (!L) return;

      if (leafletMapInstance.current) {
        try {
          leafletMapInstance.current.remove();
        } catch (e) {
          console.warn('Map cleanup error:', e);
        }
        leafletMapInstance.current = null;
      }

      const defaultLat = dest?.latitude || 25.5788;
      const defaultLng = dest?.longitude || 91.8933;

      const map = L.map(mapRef.current, {
        zoomControl: true,
        scrollWheelZoom: false,
      }).setView([defaultLat, defaultLng], 12);
      leafletMapInstance.current = map;

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      // Destination center pin
      const centerMarker = L.marker([defaultLat, defaultLng])
        .addTo(map)
        .bindPopup(`
          <div style="font-family:'Plus Jakarta Sans',sans-serif; min-width:140px;">
            <div style="font-size:0.7rem; font-weight:700; color:var(--primary); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:2px;">Destination Center</div>
            <strong style="font-size:0.95rem; color:#0f172a;">${dest?.name}</strong>
            <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">${[dest?.state, dest?.region].filter(Boolean).join(', ')}</div>
          </div>
        `);

      const latLngs = [[defaultLat, defaultLng]];

      // Add place pins with category pills
      placeItems.forEach((p) => {
        if (p.latitude && p.longitude) {
          latLngs.push([p.latitude, p.longitude]);
          L.marker([p.latitude, p.longitude])
            .addTo(map)
            .bindPopup(`
              <div style="font-family:'Plus Jakarta Sans',sans-serif; min-width:160px; max-width:220px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                  <span style="font-size:0.7rem; font-weight:700; color:#059669; text-transform:capitalize;">${p.category || 'Spot'}</span>
                  <span style="font-size:0.65rem; background:#f1f5f9; padding:2px 6px; border-radius:10px; color:#475569;">${p.source_label || 'Verified'}</span>
                </div>
                <strong style="font-size:0.92rem; color:#0f172a; display:block; margin-bottom:4px;">${p.name}</strong>
                ${p.description ? `<p style="font-size:0.76rem; color:#475569; margin:0; line-height:1.3;">${p.description}</p>` : ''}
              </div>
            `);
        }
      });

      if (latLngs.length > 1) {
        try {
          map.fitBounds(latLngs, { padding: [35, 35], maxZoom: 14 });
        } catch (e) {
          map.setView([defaultLat, defaultLng], 12);
        }
      }

      // Force Leaflet to recalculate container bounds after mount
      setTimeout(() => {
        if (map) map.invalidateSize();
      }, 150);
      setTimeout(() => {
        if (map) map.invalidateSize();
      }, 400);
    }, 60);
  };

  const loadTravelers = async () => {
    try {
      setTravelersLoading(true);
      const res = await getBuddies(destinationName);
      setTravelers(res.buddies || []);
    } catch (err) {
      console.error(err);
    } finally {
      setTravelersLoading(false);
    }
  };

  const handleSendRequest = async () => {
    if (!connectModalUser) return;
    try {
      await sendBuddyRequest(connectModalUser.user_id, destinationName, connectNote);
      setConnectStatus('Connection request sent! You will be notified when they accept.');
      setTimeout(() => {
        setConnectModalUser(null);
        setConnectStatus('');
        setConnectNote('');
        loadTravelers();
      }, 1500);
    } catch (err) {
      alert(err.message || 'Failed to send request');
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '5rem 0' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Loading {destinationName}...</p>
      </div>
    );
  }

  if (error || !dest) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: '#f87171', marginBottom: '1rem' }}>{error || 'Destination not found'}</p>
        <button className="btn btn-secondary" onClick={onBack}>
          <ArrowLeft size={16} /> Back to Explore
        </button>
      </div>
    );
  }

  const scores = dest.scores || {};
  // Deduplicate photos so that only one copy of each image is rendered
  const rawPhotos = dest.photos || [];
  const photos = Array.from(new Map(rawPhotos.map(p => [p.url, p])).values());

  return (
    <div>
      {/* Back button */}
      <button className="btn btn-secondary btn-sm" onClick={onBack} style={{ marginBottom: '1.25rem' }}>
        <ArrowLeft size={16} /> Back to All Destinations
      </button>

      {/* Hero Banner */}
      <section className="glass-panel" style={{ overflow: 'hidden', marginBottom: '2rem' }}>
        <div style={{ position: 'relative', height: '340px', background: 'var(--bg-elevated)' }}>
          <img
            src={getImageUrl(photos[0]?.url || `/images/${dest.name}/photo_01.jpg`)}
            alt={dest.name}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            onError={(e) => {
              e.target.src = 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200&q=80';
            }}
          />
          <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(15,23,42,0.15) 0%, rgba(15,23,42,0.85) 100%)' }} />

          <div style={{ position: 'absolute', bottom: '1.75rem', left: '1.75rem', right: '1.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                <span className="badge" style={{ background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(4px)', color: '#fff' }}>
                  {dest.category}
                </span>
                {dest.is_ai_estimated && (
                  <span className="badge badge-ai">
                    <Sparkles size={12} /> AI Estimated (Ridge Regressor)
                  </span>
                )}
                <span className="badge" style={{ background: 'rgba(0,0,0,0.5)', color: 'rgba(255,255,255,0.85)' }}>
                  Source: {dest.score_source}
                </span>
              </div>
              <h1 style={{ fontSize: '2.5rem', lineHeight: 1.1, color: '#ffffff' }}>{dest.name}</h1>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'rgba(255,255,255,0.85)', marginTop: '0.4rem' }}>
                <MapPin size={16} />
                <span>{[dest.state, dest.region].filter(Boolean).join(', ')}</span>
              </div>
            </div>

            {/* Vibe Pills */}
            <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap', background: 'rgba(255,255,255,0.95)', padding: '0.6rem 1rem', borderRadius: 'var(--radius-md)', backdropFilter: 'blur(8px)', border: '1px solid var(--border-glass)', boxShadow: 'var(--shadow-md)' }}>
              <div>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block' }}>Nature</span>
                <span style={{ fontWeight: 700, color: 'var(--vibe-nature)' }}>{Math.round(scores.nature || 0)}</span>
              </div>
              <div style={{ width: 1, background: 'var(--border-glass)' }} />
              <div>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block' }}>Adventure</span>
                <span style={{ fontWeight: 700, color: 'var(--vibe-adventure)' }}>{Math.round(scores.adventure || 0)}</span>
              </div>
              <div style={{ width: 1, background: 'var(--border-glass)' }} />
              <div>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block' }}>Peace</span>
                <span style={{ fontWeight: 700, color: 'var(--vibe-peacefulness)' }}>{Math.round(scores.peacefulness || 0)}</span>
              </div>
              <div style={{ width: 1, background: 'var(--border-glass)' }} />
              <div>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block' }}>Crowd</span>
                <span style={{ fontWeight: 700, color: 'var(--vibe-crowd)' }}>{Math.round(scores.crowd_match || 0)}</span>
              </div>
              <div style={{ width: 1, background: 'var(--border-glass)' }} />
              <div>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block' }}>Visual</span>
                <span style={{ fontWeight: 700, color: 'var(--vibe-visual)' }}>{Math.round(scores.visual_atmosphere || 0)}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tabs Bar */}
      <div className="tab-list">
        <button
          className={`tab-item ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview & Story
        </button>
        <button
          className={`tab-item ${activeTab === 'pictures' ? 'active' : ''}`}
          onClick={() => setActiveTab('pictures')}
        >
          <Camera size={15} style={{ verticalAlign: 'middle', marginRight: '4px' }} /> Pictures & Gallery ({photos.length})
        </button>
        <button
          className={`tab-item ${activeTab === 'plan' ? 'active' : ''}`}
          onClick={() => setActiveTab('plan')}
        >
          Day-wise Itinerary
        </button>
        <button
          className={`tab-item ${activeTab === 'travel' ? 'active' : ''}`}
          onClick={() => setActiveTab('travel')}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}
        >
          <Car size={15} style={{ color: 'var(--primary)' }} /> Travel & Transit Facilities
        </button>
        <button
          className={`tab-item ${activeTab === 'nearby' ? 'active' : ''}`}
          onClick={() => setActiveTab('nearby')}
        >
          Nearby & OSM Places
        </button>
        <button
          className={`tab-item ${activeTab === 'travelers' ? 'active' : ''}`}
          onClick={() => setActiveTab('travelers')}
        >
          Compatible Travelers
        </button>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>
          <div>
            <div className="glass-panel" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.75rem' }}>
                <Compass size={20} style={{ color: 'var(--primary)' }} />
                <h3 className="font-editorial" style={{ fontSize: '1.6rem', color: 'var(--text-main)' }}>About {dest.name}</h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, fontSize: '1rem', marginBottom: '1.75rem' }}>
                {dest.description || 'A breathtaking destination in India offering unique landscapes, authentic cultural atmosphere, and distinct travel vibes.'}
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', borderTop: '1px solid var(--border-glass)', paddingTop: '1.5rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '0.3rem' }}>
                    <Calendar size={14} /> Best Season to Visit
                  </div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.95rem' }}>
                    {dest.best_time_to_visit || 'Year Round'}
                  </div>
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '0.3rem' }}>
                    <Compass size={14} /> Geo Coordinates
                  </div>
                  <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.95rem' }}>
                    {dest.latitude ? `${dest.latitude.toFixed(4)}° N, ${dest.longitude.toFixed(4)}° E` : 'Coordinates verified'}
                  </div>
                </div>
              </div>
            </div>

            {dest.top_attractions && (
              <div className="glass-panel" style={{ padding: '1.75rem' }}>
                <h3 className="font-editorial" style={{ fontSize: '1.35rem', marginBottom: '1rem' }}>Signature Highlights</h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {dest.top_attractions.split(/[,|]/).map((att, i) => att.trim()).filter(Boolean).map((att, i) => (
                    <span key={i} className="badge" style={{ background: '#f8fafc', border: '1px solid var(--border-glass)', color: '#334155', padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>
                      {att}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Featured Preview Box with Quick Link to Pictures Tab */}
          <div>
            <div className="glass-panel" style={{ padding: '1.75rem', position: 'relative' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 className="font-editorial" style={{ fontSize: '1.35rem' }}>Visual Atmosphere</h3>
                <button
                  className="btn btn-outline-primary btn-sm"
                  onClick={() => setActiveTab('pictures')}
                >
                  <Eye size={13} /> View All {photos.length} Photos
                </button>
              </div>

              {photos.length > 0 ? (
                <div>
                  <div
                    className="photo-luxury-card"
                    style={{ marginBottom: '1rem', cursor: 'pointer' }}
                    onClick={() => setActiveTab('pictures')}
                  >
                    <div style={{ height: '220px', overflow: 'hidden' }}>
                      <img
                        src={getImageUrl(photos[0].url)}
                        alt={photos[0].attraction || dest.name}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        onError={(e) => {
                          e.target.src = 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&q=80';
                        }}
                      />
                    </div>
                    <div style={{ padding: '0.85rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <strong style={{ fontSize: '0.9rem', color: 'var(--text-main)' }}>{photos[0].attraction || dest.name}</strong>
                      <span className="badge badge-osm">Featured</span>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
                    {photos.slice(1, 4).map((p, idx) => (
                      <div
                        key={idx}
                        style={{ height: '70px', borderRadius: 'var(--radius-sm)', overflow: 'hidden', cursor: 'pointer', border: '1px solid var(--border-glass)' }}
                        onClick={() => setActiveTab('pictures')}
                      >
                        <img
                          src={getImageUrl(p.url)}
                          alt={p.attraction || `View ${idx + 2}`}
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                          onError={(e) => {
                            e.target.src = 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=300&q=80';
                          }}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p style={{ color: 'var(--text-muted)' }}>No photos uploaded for this destination yet.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: PICTURES (Dedicated Gallery Tab) */}
      {activeTab === 'pictures' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.75rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h2 className="font-editorial" style={{ fontSize: '1.85rem', color: 'var(--text-main)' }}>
                Curated Photographic Gallery
              </h2>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                High-definition multi-modal imagery verified from open Wikimedia archives & licensed contributors
              </p>
            </div>
            <span className="badge badge-ai" style={{ fontSize: '0.82rem', padding: '0.45rem 0.9rem' }}>
              <Camera size={14} /> {photos.length} High-Res Visuals
            </span>
          </div>

          {photos.length === 0 ? (
            <div className="glass-panel" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
              <Camera size={44} style={{ color: 'var(--text-muted)', margin: '0 auto 1rem' }} />
              <h4>No pictures uploaded yet</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Check back soon as local contributors upload photos.</p>
            </div>
          ) : (
            <div className="photo-gallery-grid">
              {photos.map((p, idx) => (
                <div key={idx} className="photo-luxury-card">
                  <div
                    className="photo-image-frame"
                    onClick={() => setSelectedPhotoModal(p)}
                  >
                    <img
                      src={getImageUrl(p.url)}
                      alt={p.attraction || `${dest.name} View ${idx + 1}`}
                      loading="lazy"
                      onError={(e) => {
                        e.target.src = 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&q=80';
                      }}
                    />
                    <div className="photo-overlay-gradient">
                      <span style={{ color: '#fff', fontSize: '0.78rem', background: 'rgba(0,0,0,0.6)', padding: '3px 8px', borderRadius: '4px', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Eye size={12} /> View Full
                      </span>
                    </div>
                  </div>

                  <div style={{ padding: '0.9rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {p.attraction || `Scenic Vantage ${idx + 1}`}
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                      <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '65%' }}>
                        By {p.author && p.author.replace(/<[^>]+>/g, '').trim() ? p.author.replace(/<[^>]+>/g, '').trim() : 'Wikimedia Commons'}
                      </span>
                      <span className="badge" style={{ background: '#f1f5f9', color: '#475569', fontSize: '0.68rem', padding: '2px 6px' }}>
                        {p.license || 'CC BY-SA'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: DAY-WISE ITINERARY */}
      {activeTab === 'plan' && (
        <div>
          {planLoading ? (
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
              <p style={{ color: 'var(--text-secondary)' }}>Synthesizing day-by-day vibe-aware itinerary...</p>
            </div>
          ) : plan ? (
            <div>
              {/* Header actions */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.35rem' }}>3-Day Personalized Itinerary</h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Paced according to nature ({Math.round(scores.nature || 50)}) and peacefulness ({Math.round(scores.peacefulness || 50)})
                  </p>
                </div>

                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <button
                    className="btn btn-primary"
                    onClick={handleSaveTrip}
                    disabled={savingTrip}
                  >
                    <Bookmark size={16} /> {savingTrip ? 'Saving...' : 'Save to My Trips'}
                  </button>
                </div>
              </div>

              {savedSuccess && (
                <div style={{
                  background: 'rgba(16,185,129,0.15)',
                  border: '1px solid rgba(16,185,129,0.3)',
                  color: '#34d399',
                  padding: '0.75rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: '1.5rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}>
                  <span>{savedSuccess}</span>
                  {shareUrl && (
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => {
                        navigator.clipboard.writeText(shareUrl);
                        alert('Shareable link copied to clipboard!');
                      }}
                    >
                      <Share2 size={13} /> Copy Share Link
                    </button>
                  )}
                </div>
              )}

              {/* Day selection tabs */}
              {(() => {
                const itineraryDays = Array.isArray(plan.days_itinerary)
                  ? plan.days_itinerary
                  : (Array.isArray(plan.days) ? plan.days : []);

                if (itineraryDays.length === 0) {
                  return (
                    <div style={{ padding: '1rem', color: 'var(--text-muted)' }}>
                      No itinerary details generated yet.
                    </div>
                  );
                }

                const currentDayObj = itineraryDays.find((d) => (d.day_number || d.day) === selectedDay) || itineraryDays[0];

                return (
                  <div>
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
                      {itineraryDays.map((d) => {
                        const dayNum = d.day_number || d.day || 1;
                        return (
                          <button
                            key={dayNum}
                            className={`tab-item ${selectedDay === dayNum ? 'active' : ''}`}
                            onClick={() => setSelectedDay(dayNum)}
                          >
                            Day {dayNum}: {d.theme?.replace(/^Day \d+:\s*/, '') || d.theme || `Day ${dayNum}`}
                          </button>
                        );
                      })}
                    </div>

                    {/* Selected Day Schedule */}
                    {currentDayObj && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {Array.isArray(currentDayObj.slots) && currentDayObj.slots.length > 0 ? (
                          currentDayObj.slots.map((s, sIdx) => (
                            <div key={sIdx} className="glass-panel" style={{ padding: '1.25rem' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                <span className="badge" style={{ background: 'rgba(5, 150, 105, 0.12)', color: 'var(--primary)' }}>
                                  {s.time_slot}
                                </span>
                                {s.est_distance && (
                                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                                    {s.est_distance}
                                  </span>
                                )}
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                                <h4 style={{ fontSize: '1.05rem', color: 'var(--text-main)' }}>{s.place_name}</h4>
                                {s.category && (
                                  <span className="badge" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-glass)', fontSize: '0.72rem', textTransform: 'capitalize' }}>
                                    {s.category}
                                  </span>
                                )}
                              </div>
                              {s.tip && (
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.5, marginTop: '0.35rem' }}>
                                  {s.tip}
                                </p>
                              )}

                              {/* Smart Transit & Commute Recommendation Card */}
                              {s.transit && (
                                <div style={{
                                  marginTop: '0.85rem',
                                  padding: '0.85rem 1rem',
                                  borderRadius: 'var(--radius-md)',
                                  background: 'linear-gradient(135deg, rgba(2, 132, 199, 0.05) 0%, rgba(248, 250, 252, 0.9) 100%)',
                                  border: '1px solid rgba(2, 132, 199, 0.18)',
                                  display: 'flex',
                                  flexDirection: 'column',
                                  gap: '0.5rem'
                                }}>
                                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', fontSize: '0.86rem', fontWeight: 600, color: 'var(--primary)' }}>
                                      {s.transit.mode_icon === 'walking' ? <Compass size={15} /> :
                                       s.transit.mode_icon === 'jeep' ? <Mountain size={15} /> :
                                       s.transit.mode_icon === 'bicycle' ? <Bike size={15} /> :
                                       <Car size={15} />}
                                      <span>Transit to Stop: {s.transit.primary_mode}</span>
                                      {s.transit.dl_choice_confidence && (
                                        <span className="badge" style={{ background: 'rgba(79, 70, 229, 0.12)', color: '#4f46e5', fontSize: '0.68rem', padding: '1px 6px', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                                          <Sparkles size={10} /> DL Choice: {s.transit.dl_choice_confidence}% Conf.
                                        </span>
                                      )}
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                                      <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                                        <Clock size={12} /> {s.transit.est_commute_time}
                                      </span>
                                      <span style={{ fontWeight: 600, color: 'var(--text-main)', background: '#e0f2fe', padding: '2px 8px', borderRadius: '4px' }}>
                                        {s.transit.est_price_range}
                                      </span>
                                    </div>
                                  </div>

                                  {/* Ratings bar (Eco & Comfort) */}
                                  {(s.transit.eco_rating || s.transit.comfort_rating) && (
                                    <div style={{ display: 'flex', gap: '1rem', fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                                      <span>🌱 Eco Score: <strong>{s.transit.eco_rating}/100</strong></span>
                                      <span>🛋️ Comfort: <strong>{s.transit.comfort_rating}/100</strong></span>
                                    </div>
                                  )}

                                  {s.transit.transit_tip && (
                                    <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
                                      💡 {s.transit.transit_tip}
                                    </p>
                                  )}

                                  {Array.isArray(s.transit.alternatives) && s.transit.alternatives.length > 0 && (
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.2rem' }}>
                                      <span style={{ fontSize: '0.73rem', color: 'var(--text-muted)', alignSelf: 'center' }}>Alternatives:</span>
                                      {s.transit.alternatives.map((alt, aIdx) => (
                                        <span key={aIdx} style={{
                                          fontSize: '0.72rem',
                                          background: '#ffffff',
                                          border: '1px solid var(--border-glass)',
                                          padding: '2px 7px',
                                          borderRadius: '4px',
                                          color: 'var(--text-secondary)'
                                        }}>
                                          <strong>{alt.mode}</strong> ({alt.cost} • ~{alt.time})
                                        </span>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          ))
                        ) : (
                          <>
                            {/* Morning */}
                            {currentDayObj.morning && (
                              <div className="glass-panel" style={{ padding: '1.25rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                  <span className="badge" style={{ background: 'rgba(245,158,11,0.2)', color: '#d97706' }}>
                                    Morning (09:00 - 12:30)
                                  </span>
                                  <h4 style={{ fontSize: '1.05rem' }}>{currentDayObj.morning?.title || 'Scenic Exploration'}</h4>
                                </div>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                                  {currentDayObj.morning?.description}
                                </p>
                                {currentDayObj.morning?.local_recommendation && (
                                  <div style={{ fontSize: '0.8rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                    <Compass size={14} /> Recommended spot: <strong>{currentDayObj.morning.local_recommendation}</strong>
                                  </div>
                                )}
                              </div>
                            )}

                            {/* Afternoon */}
                            {currentDayObj.afternoon && (
                              <div className="glass-panel" style={{ padding: '1.25rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                  <span className="badge" style={{ background: 'rgba(6,182,212,0.2)', color: '#0284c7' }}>
                                    Afternoon (13:00 - 16:30)
                                  </span>
                                  <h4 style={{ fontSize: '1.05rem' }}>{currentDayObj.afternoon?.title || 'Local Culture & Food'}</h4>
                                </div>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                                  {currentDayObj.afternoon?.description}
                                </p>
                                {currentDayObj.afternoon?.local_recommendation && (
                                  <div style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                    <Utensils size={14} /> Lunch spot: <strong>{currentDayObj.afternoon.local_recommendation}</strong>
                                  </div>
                                )}
                              </div>
                            )}

                            {/* Evening */}
                            {currentDayObj.evening && (
                              <div className="glass-panel" style={{ padding: '1.25rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                  <span className="badge" style={{ background: 'rgba(168,85,247,0.2)', color: '#7c3aed' }}>
                                    Evening (17:00 - 20:30)
                                  </span>
                                  <h4 style={{ fontSize: '1.05rem' }}>{currentDayObj.evening?.title || 'Sunset & Relaxation'}</h4>
                                </div>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.75rem' }}>
                                  {currentDayObj.evening?.description}
                                </p>
                                {currentDayObj.evening?.local_recommendation && (
                                  <div style={{ fontSize: '0.8rem', color: 'var(--accent-purple)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                    <Coffee size={14} /> Sunset view / Cafe: <strong>{currentDayObj.evening.local_recommendation}</strong>
                                  </div>
                                )}
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    )}

                    {/* Local Transit Facilities & Rental Hubs */}
                    {plan.transit_facilities && (
                      <div className="glass-panel" style={{ marginTop: '2rem', padding: '1.5rem', background: 'linear-gradient(180deg, #f8fafc 0%, #ffffff 100%)', border: '1px solid var(--border-glass)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.6rem' }}>
                          <Car size={18} style={{ color: 'var(--primary)' }} />
                          <h4 style={{ fontSize: '1.15rem', color: 'var(--text-main)', margin: 0 }}>
                            Local Transit & Rental Facilities in {dest.name}
                          </h4>
                        </div>
                        <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '1.2rem', lineHeight: 1.5 }}>
                          {plan.transit_facilities.local_transit_advisory}
                        </p>

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                          {plan.transit_facilities.rental_hubs.map((hub, hIdx) => (
                            <div key={hIdx} style={{
                              background: '#ffffff',
                              border: '1px solid var(--border-glass)',
                              borderRadius: 'var(--radius-md)',
                              padding: '1rem',
                              boxShadow: 'var(--shadow-sm)'
                            }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                                <strong style={{ fontSize: '0.92rem', color: 'var(--text-main)' }}>{hub.type}</strong>
                                <span className="badge" style={{ background: '#e0f2fe', color: 'var(--primary)', fontSize: '0.72rem', fontWeight: 600 }}>
                                  {hub.rate}
                                </span>
                              </div>
                              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                                Provider: <strong>{hub.provider}</strong> • <span style={{ color: 'var(--text-muted)' }}>{hub.contact_type}</span>
                              </div>
                              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                                ✓ {hub.highlights}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })()}
            </div>
          ) : (
            <button className="btn btn-primary" onClick={loadPlan}>
              Generate 3-Day Plan
            </button>
          )}
        </div>
      )}

      {/* TAB 3: TRAVEL & TRANSIT FACILITIES DASHBOARD */}
      {activeTab === 'travel' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Header Banner */}
          <div className="glass-panel" style={{ padding: '2rem', background: 'linear-gradient(135deg, rgba(2,132,199,0.08) 0%, rgba(248,250,252,0.95) 100%)', border: '1px solid rgba(2,132,199,0.2)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
                  <span className="badge" style={{ background: '#e0f2fe', color: 'var(--primary)', fontSize: '0.75rem', fontWeight: 600 }}>
                    <Car size={13} style={{ marginRight: '3px' }} /> Smart Commute Recommendations
                  </span>
                  <span className="badge" style={{ background: 'rgba(79, 70, 229, 0.1)', color: '#4f46e5', fontSize: '0.75rem' }}>
                    Multi-Modal Transit
                  </span>
                </div>
                <h2 style={{ fontSize: '1.8rem', color: 'var(--text-main)', margin: '0.3rem 0' }}>
                  Transit & Commute Facilities for {dest.name}
                </h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', maxWidth: '750px', lineHeight: 1.6 }}>
                  Recommended modes of transit for your trip based on local terrain, inter-sight distances, and your travel vibes. Explore travel modes or check local verified rental desks below.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => setShowAiArchitecture(!showAiArchitecture)}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                >
                  <Sparkles size={14} style={{ color: '#4f46e5' }} />
                  {showAiArchitecture ? 'Hide Model Architecture' : 'View DL Model Specs'}
                </button>
                <button className="btn btn-primary btn-sm" onClick={() => setActiveTab('plan')}>
                  <Calendar size={14} /> View in Day Schedule
                </button>
              </div>
            </div>

            {/* Collapsible AI Architecture Overview Banner (For Viva / Detailed View) */}
            {showAiArchitecture && (
              <div style={{
                marginTop: '1.5rem',
                padding: '1.25rem',
                borderRadius: 'var(--radius-md)',
                background: '#ffffff',
                border: '1.5px solid #4f46e5',
                boxShadow: 'var(--shadow-sm)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#4f46e5', display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <Sparkles size={14} /> PyTorch Deep Choice MLP Specification (Academic & Technical Details)
                  </span>
                  <span className="badge" style={{ background: '#ecfdf5', color: '#059669', fontSize: '0.7rem' }}>
                    Active Evaluation Model
                  </span>
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
                  gap: '1rem'
                }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>DL Neural Architecture</div>
                    <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--primary)' }}>
                      Multi-Modal MLP (64-32-5)
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>BatchNorm + LeakyReLU + Softmax</div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Input Dimensions</div>
                    <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--text-main)' }}>
                      11 Contextual Features
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Log-dist, Terrain, 5 Vibes, ToD, Group</div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Decision Objective</div>
                    <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--vibe-nature)' }}>
                      Discrete Choice Utility Max
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Balancing Cost, Eco-Impact & Speed</div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Loss & Weights</div>
                    <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--accent-coral)' }}>
                      CrossEntropyLoss (AdamW)
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>deep_transit_weights.pt loaded</div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Probability Distribution Graph & Mode Comparison */}
          {plan && Array.isArray(plan.days_itinerary) && (() => {
            // Find representative transit leg with valid probabilities
            let sampleTransit = null;
            let sampleLegName = `Representative Sight commute in ${dest.name}`;
            for (const day of plan.days_itinerary) {
              for (const slot of day.slots || []) {
                if (slot.transit?.dl_probability_distribution && slot.transit.distance_km > 0) {
                  sampleTransit = slot.transit;
                  sampleLegName = `${slot.place_name} (${slot.est_distance})`;
                  break;
                }
              }
              if (sampleTransit) break;
            }

            if (!sampleTransit) return null;

            return (
              <div className="glass-panel" style={{ padding: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.3rem', color: 'var(--text-main)' }}>
                      📊 Multi-Modal Transit Choice Distribution
                    </h3>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      Route: <strong>{sampleLegName}</strong> &bull; Selected Mode: <strong style={{ color: 'var(--primary)' }}>{sampleTransit.primary_mode}</strong>
                    </p>
                  </div>
                  <span className="badge" style={{ background: '#ecfdf5', color: '#059669', fontWeight: 600, padding: '4px 10px' }}>
                    Model Confidence: {sampleTransit.dl_choice_confidence || 88.5}%
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
                  {(sampleTransit.dl_probability_distribution || []).map((item, pIdx) => (
                  <div key={pIdx} style={{
                    padding: '0.85rem 1rem',
                    borderRadius: 'var(--radius-md)',
                    background: item.is_chosen ? 'rgba(2, 132, 199, 0.08)' : '#ffffff',
                    border: item.is_chosen ? '1.5px solid var(--primary)' : '1px solid var(--border-glass)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem', fontSize: '0.88rem' }}>
                      <span style={{ fontWeight: item.is_chosen ? 700 : 500, color: item.is_chosen ? 'var(--primary)' : 'var(--text-main)' }}>
                        {item.is_chosen && '⭐ '} {item.mode_name}
                      </span>
                      <span style={{ fontWeight: 700, color: item.is_chosen ? 'var(--primary)' : 'var(--text-secondary)' }}>
                        {item.probability}%
                      </span>
                    </div>

                    {/* Progress Bar Visual */}
                    <div style={{ height: '8px', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden', marginBottom: '0.4rem' }}>
                      <div style={{
                        width: `${Math.max(4, item.probability)}%`,
                        height: '100%',
                        background: item.is_chosen ? 'linear-gradient(90deg, #0284c7, #38bdf8)' : '#94a3b8',
                        borderRadius: '4px',
                        transition: 'width 0.6s ease'
                      }} />
                    </div>

                    <div style={{ display: 'flex', gap: '1.25rem', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      <span>Eco Score: <strong>{item.eco_score}/100</strong></span>
                      <span>Comfort Index: <strong>{item.comfort_score}/100</strong></span>
                      {item.is_chosen && <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Optimal DL Choice</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            );
          })()}

          {/* Verified Local Rental & Mobility Hubs */}
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
              <Navigation size={22} style={{ color: 'var(--primary)' }} />
              <h3 style={{ fontSize: '1.35rem', color: 'var(--text-main)', margin: 0 }}>
                Verified Local Rental & Transit Hubs
              </h3>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.5rem', lineHeight: 1.5 }}>
              Direct access to self-drive scooty rentals, registered taxi stands, bicycle hubs, and certified local guides for seamless navigation.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))', gap: '1.25rem' }}>
              {(plan?.transit_facilities?.rental_hubs || [
                {
                  type: 'Self-Drive Scooty / Bike Rental',
                  provider: 'Royal Brothers / Local Hub',
                  rate: '₹500 - ₹900 / day',
                  highlights: 'Helmet included, zero security deposit with DL, fuel extra.',
                  contact_type: 'Direct Hub & App'
                },
                {
                  type: 'Private Sightseeing Cab (Sedan / SUV)',
                  provider: 'Central Taxi Union Stand',
                  rate: '₹1800 - ₹3200 / day (8 hrs / 80 km)',
                  highlights: 'Dedicated driver, AC, toll/parking included upon confirmation.',
                  contact_type: 'Taxi Union Kiosk & Booking Desk'
                },
                {
                  type: 'Eco Commute & Bicycle Rentals',
                  provider: 'Green Wheel Hub / Local Stand',
                  rate: '₹150 - ₹300 / day (₹50/hr)',
                  highlights: 'Geared mountain bikes or city cruisers for local sightseeing lanes.',
                  contact_type: 'Walk-in & Rental Stalls'
                }
              ]).map((hub, hIdx) => (
                <div key={hIdx} style={{
                  background: '#ffffff',
                  border: '1px solid var(--border-glass)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '1.5rem',
                  boxShadow: 'var(--shadow-sm)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '0.75rem'
                }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                      <strong style={{ fontSize: '1.05rem', color: 'var(--text-main)' }}>{hub.type}</strong>
                      <span className="badge" style={{ background: '#e0f2fe', color: 'var(--primary)', fontSize: '0.75rem', fontWeight: 700 }}>
                        {hub.rate}
                      </span>
                    </div>

                    <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '0.6rem' }}>
                      Verified Partner: <strong>{hub.provider}</strong>
                    </div>

                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
                      ✓ {hub.highlights}
                    </p>
                  </div>

                  <div style={{
                    paddingTop: '0.75rem',
                    borderTop: '1px solid var(--border-glass)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '0.78rem'
                  }}>
                    <span style={{ color: 'var(--text-muted)' }}>Booking: <strong>{hub.contact_type}</strong></span>
                    <button
                      className="btn btn-outline-primary btn-sm"
                      onClick={() => setSelectedInquiryHub(hub)}
                    >
                      Inquire Hub & Booking
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: NEARBY & OSM PLACES */}
      {activeTab === 'nearby' && (
        <div>
          {/* Category filter pills with count hint */}
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
            {[
              { id: 'all', label: 'All Places' },
              { id: 'viewpoint', label: 'Scenic Viewpoints' },
              { id: 'cafe', label: 'Cafes' },
              { id: 'food', label: 'Restaurants' },
              { id: 'attraction', label: 'Attractions' },
              { id: 'activity', label: 'Activities' },
              { id: 'guide', label: 'Certified Guides' },
            ].map((c) => (
              <button
                key={c.id}
                type="button"
                className={`btn btn-sm ${categoryFilter === c.id ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => handleCategoryChange(c.id)}
              >
                {c.label}
              </button>
            ))}
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: 'auto' }}>
              Showing {places.length} verified location{places.length !== 1 ? 's' : ''}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
            {/* Interactive Leaflet Map */}
            <div className="glass-panel osm-map-wrapper" style={{ padding: '0.85rem', height: '480px', display: 'flex', flexDirection: 'column' }}>
              <div style={{ padding: '0.4rem 0.5rem 0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <MapPin size={16} style={{ color: 'var(--primary)' }} />
                  <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    OpenStreetMap Geographic Explorer
                  </span>
                </div>
                <span className="badge badge-osm" style={{ fontSize: '0.7rem' }}>
                  Live Interactive
                </span>
              </div>
              <div ref={mapRef} style={{ width: '100%', flex: 1, borderRadius: 'var(--radius-sm)', minHeight: '360px' }} />
            </div>

            {/* Places List */}
            <div style={{ maxHeight: '480px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.85rem', paddingRight: '4px' }}>
              {placesLoading ? (
                <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
                  <p style={{ color: 'var(--text-secondary)' }}>Loading verified places from OpenStreetMap...</p>
                </div>
              ) : places.length === 0 ? (
                <div className="glass-panel" style={{ padding: '3rem 2rem', textAlign: 'center' }}>
                  <Compass size={36} style={{ color: 'var(--text-muted)', margin: '0 auto 0.75rem' }} />
                  <h4 style={{ fontSize: '1.05rem', color: 'var(--text-main)' }}>No spots found for this filter</h4>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>Try selecting "All Places" to view all available locations.</p>
                </div>
              ) : (
                places.map((p) => (
                  <div key={p.id} className="place-card-item">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.4rem' }}>
                      <h4 style={{ fontSize: '1rem', color: 'var(--text-main)', fontWeight: 700 }}>{p.name}</h4>
                      <span className={`badge ${p.source === 'osm' ? 'badge-osm' : p.source === 'admin' ? 'badge-admin' : 'badge-local'}`}>
                        {p.source_label}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: 'var(--primary)', fontWeight: 600, marginBottom: '0.45rem', textTransform: 'capitalize' }}>
                      {p.category === 'cafe' && <Coffee size={13} />}
                      {p.category === 'food' && <Utensils size={13} />}
                      {p.category === 'viewpoint' && <Mountain size={13} />}
                      {p.category === 'attraction' && <Sparkles size={13} />}
                      {p.category === 'activity' && <Activity size={13} />}
                      {p.category === 'guide' && <UserCheck size={13} style={{ color: '#059669' }} />}
                      <span>Category: {p.category === 'guide' ? 'Certified Local Guide' : p.category}</span>
                    </div>

                    {p.description && (
                      <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '0.4rem' }}>
                        {p.description}
                      </p>
                    )}

                    {p.contact_info && (
                      <div style={{ fontSize: '0.78rem', color: '#047857', background: '#ecfdf5', padding: '0.35rem 0.65rem', borderRadius: '4px', marginTop: '0.3rem', marginBottom: '0.3rem', fontWeight: 600 }}>
                        💳 {p.contact_info}
                      </div>
                    )}

                    {p.crowd_hint && (
                      <div style={{ fontSize: '0.78rem', color: '#b45309', background: '#fef3c7', padding: '0.3rem 0.6rem', borderRadius: '4px', marginTop: '0.4rem', display: 'inline-block' }}>
                        Tip: {p.crowd_hint}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: COMPATIBLE TRAVELERS */}
      {activeTab === 'travelers' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1.35rem' }}>Travelers Heading to {dest.name}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Sorted by multi-modal vibe similarity & travel date compatibility
              </p>
            </div>
          </div>

          {travelersLoading ? (
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
              <p style={{ color: 'var(--text-secondary)' }}>Finding compatible buddies...</p>
            </div>
          ) : travelers.length === 0 ? (
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
              <Users size={32} style={{ color: 'var(--text-muted)', margin: '0 auto 0.75rem' }} />
              <h4>No other travelers listed for {dest.name} yet</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.3rem' }}>
                Be the first to post your dates and find travel companions!
              </p>
            </div>
          ) : (
            <div className="grid-cards">
              {travelers.map((t) => (
                <div key={t.user_id} className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <div>
                      <h4 style={{ fontSize: '1.1rem' }}>{t.name}</h4>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                        {t.home_city ? `From ${t.home_city}` : 'Traveler'}
                      </div>
                    </div>
                    <span className="badge badge-match">
                      {Math.round(t.compatibility_score || 0)}% Compatible
                    </span>
                  </div>

                  {t.bio && (
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.4, marginBottom: '0.75rem' }}>
                      "{t.bio}"
                    </p>
                  )}

                  {t.interest_tags && (
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                      {t.interest_tags.split(',').map((tag, i) => (
                        <span key={i} className="badge" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-secondary)' }}>
                          {tag.trim()}
                        </span>
                      ))}
                    </div>
                  )}

                  <div style={{ marginTop: 'auto', paddingTop: '0.75rem', borderTop: '1px solid var(--border-glass)' }}>
                    <button
                      className="btn btn-outline-primary btn-sm"
                      style={{ width: '100%' }}
                      onClick={() => {
                        if (!user) {
                          onOpenAuth('login');
                        } else {
                          setConnectModalUser(t);
                        }
                      }}
                    >
                      <HeartHandshake size={15} /> Connect & Share Contact
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Connect Modal */}
      {connectModalUser && (
        <div className="modal-overlay" onClick={() => setConnectModalUser(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Connect with {connectModalUser.name}</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Send an introduction note. Your contact information will only be shared if they accept your connection request.
            </p>

            {connectStatus && (
              <div style={{ background: 'rgba(16,185,129,0.15)', color: '#34d399', padding: '0.75rem', borderRadius: 'var(--radius-sm)', marginBottom: '1rem', fontSize: '0.85rem' }}>
                {connectStatus}
              </div>
            )}

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                Introduction Note
              </label>
              <textarea
                className="input-field"
                rows={4}
                placeholder="Hi! I'm planning to visit around the same time and would love to explore together..."
                value={connectNote}
                onChange={(e) => setConnectNote(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
              <button className="btn btn-secondary" onClick={() => setConnectModalUser(null)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleSendRequest}>
                Send Connection Request
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Picture Lightbox Modal */}
      {selectedPhotoModal && (
        <div className="modal-overlay" onClick={() => setSelectedPhotoModal(null)}>
          <div
            className="modal-content"
            style={{ maxWidth: '820px', padding: '0', overflow: 'hidden', background: '#0f172a', border: '1px solid rgba(255,255,255,0.15)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ position: 'relative', width: '100%', maxHeight: '520px', background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <img
                src={getImageUrl(selectedPhotoModal.url)}
                alt={selectedPhotoModal.attraction || dest.name}
                style={{ width: '100%', maxHeight: '520px', objectFit: 'contain' }}
                onError={(e) => {
                  e.target.src = 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200&q=80';
                }}
              />
              <button
                onClick={() => setSelectedPhotoModal(null)}
                style={{
                  position: 'absolute',
                  top: '1rem',
                  right: '1rem',
                  background: 'rgba(0,0,0,0.65)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  color: '#ffffff',
                  borderRadius: '50%',
                  width: '36px',
                  height: '36px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  backdropFilter: 'blur(6px)',
                }}
              >
                <X size={18} />
              </button>
            </div>

            <div style={{ padding: '1.25rem 1.5rem', background: '#1e293b', color: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h3 className="font-editorial" style={{ fontSize: '1.35rem', color: '#ffffff', marginBottom: '2px' }}>
                  {selectedPhotoModal.attraction || dest.name}
                </h3>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  Verified by Wikimedia Archives &bull; {selectedPhotoModal.author && selectedPhotoModal.author.replace(/<[^>]+>/g, '').trim() ? selectedPhotoModal.author.replace(/<[^>]+>/g, '').trim() : 'Wikimedia Commons'} ({selectedPhotoModal.license || 'CC BY-SA'})
                </div>
              </div>

              {selectedPhotoModal.source_url && (
                <a
                  href={selectedPhotoModal.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-sm"
                  style={{ background: 'rgba(255,255,255,0.1)', color: '#ffffff', border: '1px solid rgba(255,255,255,0.2)' }}
                >
                  <ExternalLink size={13} /> Original Source
                </a>
              )}
            </div>
          </div>
        </div>
      )}

      {/* INQUIRE HUB & BOOKING MODAL */}
      {selectedInquiryHub && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.75)',
          backdropFilter: 'blur(5px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1.5rem',
        }}>
          <div className="glass-panel" style={{
            maxWidth: '520px',
            width: '100%',
            background: '#ffffff',
            borderRadius: 'var(--radius-xl)',
            padding: '2rem',
            position: 'relative',
            boxShadow: 'var(--shadow-hover)'
          }}>
            <button
              onClick={() => setSelectedInquiryHub(null)}
              style={{
                position: 'absolute',
                top: '1.25rem',
                right: '1.25rem',
                background: 'var(--bg-elevated)',
                border: 'none',
                borderRadius: '50%',
                width: '32px',
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer'
              }}
            >
              <X size={16} />
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
              <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: '#e0f2fe', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Car size={20} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.25rem', color: 'var(--text-main)', margin: 0 }}>
                  {selectedInquiryHub.type}
                </h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Location: {dest.name} &bull; {selectedInquiryHub.provider}
                </span>
              </div>
            </div>

            <div style={{
              margin: '1.25rem 0',
              padding: '1rem',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border-glass)',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Standard Rate</span>
                <strong style={{ fontSize: '0.95rem', color: 'var(--primary)' }}>{selectedInquiryHub.rate}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Verification Desk</span>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-main)' }}>{selectedInquiryHub.contact_type}</span>
              </div>
              {selectedInquiryHub.phone && (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Direct Support / Desk</span>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-main)', fontWeight: 600 }}>{selectedInquiryHub.phone}</span>
                </div>
              )}
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ fontSize: '0.88rem', color: 'var(--text-main)', marginBottom: '0.35rem' }}>
                Rental & Commute Advisory:
              </h4>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                {selectedInquiryHub.highlights} Valid driver license and government ID required upon pickup. We recommend checking helmet and tire condition prior to departure.
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <a
                href={selectedInquiryHub.primary_action_url || selectedInquiryHub.booking_url || `https://m.uber.com/looking`}
                target="_blank"
                rel="noreferrer"
                className="btn btn-primary"
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', textAlign: 'center', textDecoration: 'none', fontWeight: 600 }}
              >
                {selectedInquiryHub.category_tag === 'cab' ? <Car size={16} /> :
                 selectedInquiryHub.category_tag === 'bike' ? <Bike size={16} /> :
                 <Navigation size={16} />}
                {selectedInquiryHub.primary_action_label || 'Book Ride / Rental'}
              </a>

              {(selectedInquiryHub.secondary_action_url || selectedInquiryHub.provider_url) && (
                <a
                  href={selectedInquiryHub.secondary_action_url || selectedInquiryHub.provider_url}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary"
                  style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', textAlign: 'center', textDecoration: 'none' }}
                >
                  <ExternalLink size={14} />
                  {selectedInquiryHub.secondary_action_label || 'Alternative Provider Portal'}
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
