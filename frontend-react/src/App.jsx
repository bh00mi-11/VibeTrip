import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AuthModal from './components/AuthModal';
import VibeControls from './components/VibeControls';
import DestinationCard from './components/DestinationCard';
import DestinationDetail from './components/DestinationDetail';
import SavedTripsView from './components/SavedTripsView';
import InboxView from './components/InboxView';
import ContributorView from './components/ContributorView';
import AdminPortalView from './components/AdminPortalView';
import SubmitPlaceModal from './components/SubmitPlaceModal';
import { getUser, logout, recommendDestinations } from './api';
import { Sparkles, MapPin, Compass, Search, Calendar, Trees, Building2, Palmtree, Mountain } from 'lucide-react';

export default function App() {
  const [user, setUser] = useState(getUser());
  const [currentView, setCurrentView] = useState('explore');
  const [selectedDestination, setSelectedDestination] = useState(null);

  // Search & Filter state
  const [activeCategory, setActiveCategory] = useState('all');
  const [tripPace, setTripPace] = useState('balanced');
  const [selectedSeason, setSelectedSeason] = useState('any');

  // Vibe state
  const [vibes, setVibes] = useState({
    nature: 'high',
    adventure: 'medium',
    peacefulness: 'high',
    crowd_match: 'medium',
    visual_atmosphere: 'high',
  });
  const [queryText, setQueryText] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  // Modals
  const [authModal, setAuthModal] = useState({ open: false, tab: 'login' });
  const [submitPlaceOpen, setSubmitPlaceOpen] = useState(false);

  // Load initial destinations
  useEffect(() => {
    fetchRecommendations(vibes, queryText);
  }, []);

  // If admin logs in, go to admin console; if guide or local logs in, go to their requests & submissions
  useEffect(() => {
    if (user?.role === 'admin' && currentView !== 'destination') {
      setCurrentView('admin');
    } else if ((user?.role === 'guide' || user?.role === 'local') && currentView === 'explore') {
      setCurrentView('inbox');
    }
  }, [user]);

  const fetchRecommendations = async (targetVibes, q = queryText) => {
    try {
      setLoading(true);
      const res = await recommendDestinations(targetVibes, q);
      setRecommendations(res.recommendations || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleVibeChange = (newVibes) => {
    setVibes(newVibes);
  };

  const handlePresetSelect = (presetVibes) => {
    setVibes(presetVibes);
    fetchRecommendations(presetVibes, queryText);
  };

  const handleSearch = () => {
    fetchRecommendations(vibes, queryText);
  };

  const handleSelectDestination = (name) => {
    setSelectedDestination(name);
    setCurrentView('destination');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLogout = () => {
    logout();
    setUser(null);
    setCurrentView('explore');
  };

  return (
    <div className="app-root">
      {/* Top Navigation */}
      <Navbar
        user={user}
        currentView={currentView}
        onViewChange={(view) => {
          setCurrentView(view);
          if (view !== 'destination') setSelectedDestination(null);
        }}
        onOpenAuth={(tab) => setAuthModal({ open: true, tab })}
        onOpenSubmitPlace={() => {
          if (!user) {
            setAuthModal({ open: true, tab: 'login' });
          } else {
            setSubmitPlaceOpen(true);
          }
        }}
        onLogout={handleLogout}
      />

      {/* Main View Area */}
      <main style={{ maxWidth: '1320px', margin: '0 auto', padding: '2rem 1.5rem' }}>
        {/* VIEW 1: EXPLORE (HOME) */}
        {currentView === 'explore' && (
          <div>
            {/* Travel Platform Hero Header with Integrated Booking Search */}
            <div className="travel-hero-section">
              <div style={{ maxWidth: '840px', margin: '0 auto', textAlign: 'center' }}>
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  background: 'rgba(255, 255, 255, 0.12)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  padding: '0.35rem 0.85rem',
                  borderRadius: '9999px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  color: '#e2e8f0',
                  marginBottom: '1rem',
                  backdropFilter: 'blur(4px)'
                }}>
                  <Compass size={14} style={{ color: '#38bdf8' }} /> Explore 51 Verified Destinations across India
                </span>

                <h1 style={{ fontSize: '2.8rem', fontWeight: 800, lineHeight: 1.15, color: '#ffffff', letterSpacing: '-0.02em', marginBottom: '0.75rem' }}>
                  Discover Your Next Getaway
                </h1>
                <p style={{ color: '#cbd5e1', fontSize: '1.05rem', lineHeight: 1.6, maxWidth: '620px', margin: '0 auto' }}>
                  Smart itinerary planning, verified OpenStreetMap spots, local activities, and curated travel experiences tailored to your travel style.
                </p>
              </div>

              {/* Realistic Booking & Destination Search Bar */}
              <div className="booking-search-card">
                {/* Search Category Tabs */}
                <div className="booking-category-tabs">
                  {[
                    { id: 'all', label: 'All Destinations', icon: Compass },
                    { id: 'nature', label: 'Hills & Nature', icon: Trees },
                    { id: 'heritage', label: 'Heritage & Culture', icon: Building2 },
                    { id: 'beach', label: 'Coastal & Beaches', icon: Palmtree },
                    { id: 'adventure', label: 'Adventure Sports', icon: Mountain },
                  ].map((cat) => {
                    const CatIcon = cat.icon;
                    return (
                      <button
                        key={cat.id}
                        type="button"
                        className={`booking-cat-btn ${activeCategory === cat.id ? 'active' : ''}`}
                        onClick={() => {
                          setActiveCategory(cat.id);
                          if (cat.id === 'all') {
                            setQueryText('');
                            fetchRecommendations(vibes, '');
                          } else {
                            setQueryText(cat.label);
                            fetchRecommendations(vibes, cat.label);
                          }
                        }}
                      >
                        <CatIcon size={14} /> {cat.label}
                      </button>
                    );
                  })}
                </div>

                {/* Search Inputs Grid */}
                <div className="booking-search-grid">
                  {/* Destination / Search Term */}
                  <div className="booking-input-box">
                    <label>Where to?</label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                      <MapPin size={17} style={{ color: 'var(--primary)', flexShrink: 0 }} />
                      <input
                        type="text"
                        placeholder="Search places, landscapes, or activities (e.g. Manali, Tea gardens, Kayaking)..."
                        value={queryText}
                        onChange={(e) => setQueryText(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                      />
                    </div>
                  </div>

                  {/* Trip Style */}
                  <div className="booking-input-box">
                    <label>Travel Pace</label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                      <Compass size={17} style={{ color: '#f59e0b', flexShrink: 0 }} />
                      <select
                        value={tripPace}
                        onChange={(e) => {
                          setTripPace(e.target.value);
                          if (e.target.value === 'relaxed') {
                            const newV = { ...vibes, peacefulness: 'high', crowd_match: 'low' };
                            setVibes(newV);
                            fetchRecommendations(newV, queryText);
                          } else if (e.target.value === 'active') {
                            const newV = { ...vibes, adventure: 'high', nature: 'high' };
                            setVibes(newV);
                            fetchRecommendations(newV, queryText);
                          } else {
                            const newV = { ...vibes, peacefulness: 'medium', adventure: 'medium' };
                            setVibes(newV);
                            fetchRecommendations(newV, queryText);
                          }
                        }}
                      >
                        <option value="balanced">Balanced Exploration</option>
                        <option value="relaxed">Slow & Peaceful</option>
                        <option value="active">Active & Adventurous</option>
                      </select>
                    </div>
                  </div>

                  {/* Best Season */}
                  <div className="booking-input-box">
                    <label>When?</label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                      <Calendar size={17} style={{ color: '#0d9488', flexShrink: 0 }} />
                      <select
                        value={selectedSeason}
                        onChange={(e) => {
                          setSelectedSeason(e.target.value);
                          if (e.target.value !== 'any') {
                            fetchRecommendations(vibes, `${queryText} ${e.target.value}`.trim());
                          } else {
                            fetchRecommendations(vibes, queryText);
                          }
                        }}
                      >
                        <option value="any">Any Time of Year</option>
                        <option value="winter">Winter (Oct - Feb)</option>
                        <option value="summer">Summer (Mar - Jun)</option>
                        <option value="monsoon">Monsoon (Jul - Sep)</option>
                      </select>
                    </div>
                  </div>

                  {/* Search Button */}
                  <button
                    className="btn btn-primary"
                    onClick={handleSearch}
                    disabled={loading}
                    style={{
                      height: '52px',
                      padding: '0 1.75rem',
                      fontSize: '0.95rem',
                      fontWeight: 700,
                      borderRadius: 'var(--radius-md)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    <Search size={18} />
                    {loading ? 'Searching...' : 'Explore Places'}
                  </button>
                </div>
              </div>
            </div>

            {/* Travel Style Filter Controls */}
            <VibeControls
              vibes={vibes}
              onChange={handleVibeChange}
              onPresetSelect={handlePresetSelect}
              queryText={queryText}
              onQueryChange={setQueryText}
              onSearch={handleSearch}
              loading={loading}
            />

            {/* Recommendations Grid */}
            <section>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div>
                  <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0f172a' }}>
                    Featured Travel Destinations
                  </h2>
                  <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                    Handpicked destinations matching your selected preferences and travel pacing
                  </p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ fontSize: '0.85rem', color: '#64748b', background: '#ffffff', padding: '0.35rem 0.75rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <strong>{recommendations.length}</strong> destinations available
                  </span>
                </div>
              </div>

              {loading ? (
                <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 'var(--radius-lg)', padding: '4rem 2rem', textAlign: 'center' }}>
                  <p style={{ color: '#64748b', fontSize: '0.95rem' }}>Finding top matching destinations across India...</p>
                </div>
              ) : recommendations.length === 0 ? (
                <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: 'var(--radius-lg)', padding: '3.5rem 2rem', textAlign: 'center' }}>
                  <p style={{ color: '#64748b', fontSize: '0.95rem' }}>No destinations matched your search query. Try choosing "All Destinations" or clearing search terms.</p>
                </div>
              ) : (
                <div className="grid-cards">
                  {recommendations.map((dest) => (
                    <DestinationCard
                      key={dest.name}
                      dest={dest}
                      onSelect={handleSelectDestination}
                    />
                  ))}
                </div>
              )}
            </section>
          </div>
        )}

        {/* VIEW 2: DESTINATION DEEP DIVE */}
        {currentView === 'destination' && selectedDestination && (
          <DestinationDetail
            destinationName={selectedDestination}
            user={user}
            onBack={() => {
              setCurrentView('explore');
              setSelectedDestination(null);
            }}
            onOpenAuth={(tab) => setAuthModal({ open: true, tab })}
          />
        )}

        {/* VIEW 3: SAVED TRIPS */}
        {currentView === 'trips' && (
          <SavedTripsView onSelectDestination={handleSelectDestination} />
        )}

        {/* VIEW 4: INBOX */}
        {currentView === 'inbox' && (
          <InboxView user={user} />
        )}

        {/* VIEW 5: CONTRIBUTOR SUBMISSIONS */}
        {currentView === 'contribute' && (
          <ContributorView user={user} onOpenSubmitModal={() => setSubmitPlaceOpen(true)} />
        )}

        {/* VIEW 6: ADMIN PORTAL */}
        {currentView === 'admin' && (
          <AdminPortalView />
        )}
      </main>

      {/* Auth Modal */}
      {authModal.open && (
        <AuthModal
          initialTab={authModal.tab}
          onClose={() => setAuthModal({ open: false, tab: 'login' })}
          onSuccess={(u) => setUser(u)}
        />
      )}

      {/* Submit Place Modal */}
      {submitPlaceOpen && (
        <SubmitPlaceModal
          onClose={() => setSubmitPlaceOpen(false)}
          onSuccess={() => {
            if (currentView === 'contribute') {
              // will trigger re-fetch if in contributor view
            }
          }}
        />
      )}
    </div>
  );
}
