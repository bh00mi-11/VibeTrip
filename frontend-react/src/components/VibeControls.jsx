import React, { useState } from 'react';
import { Trees, Mountain, Feather, Users, Sparkles, SlidersHorizontal, ChevronDown, ChevronUp, Search, X, Camera } from 'lucide-react';

const VIBE_DIMS = [
  { key: 'nature', label: 'Nature & Scenery', icon: Trees, color: 'var(--vibe-nature)', desc: 'Lush landscapes, hills & greenery' },
  { key: 'adventure', label: 'Outdoor Adventure', icon: Mountain, color: 'var(--vibe-adventure)', desc: 'Trekking, sports & trails' },
  { key: 'peacefulness', label: 'Peace & Serenity', icon: Feather, color: 'var(--vibe-peacefulness)', desc: 'Quiet escapes & calm pace' },
  { key: 'crowd_match', label: 'Pace & Density', icon: Users, color: 'var(--vibe-crowd)', desc: 'Low: offbeat; High: lively buzz' },
  { key: 'visual_atmosphere', label: 'Scenic Aesthetics', icon: Sparkles, color: 'var(--vibe-visual)', desc: 'Iconic architecture & vistas' },
];

const PRESETS = [
  {
    name: '🌲 Nature Retreat',
    vibes: { nature: 'high', adventure: 'low', peacefulness: 'high', crowd_match: 'low', visual_atmosphere: 'high' }
  },
  {
    name: '🧗 Outdoor Adventure',
    vibes: { nature: 'high', adventure: 'high', peacefulness: 'low', crowd_match: 'high', visual_atmosphere: 'high' }
  },
  {
    name: '🌆 Culture & Heritage',
    vibes: { nature: 'medium', adventure: 'medium', peacefulness: 'low', crowd_match: 'high', visual_atmosphere: 'high' }
  },
  {
    name: '🧘 Peaceful Solitude',
    vibes: { nature: 'high', adventure: 'medium', peacefulness: 'high', crowd_match: 'low', visual_atmosphere: 'high' }
  }
];

export default function VibeControls({
  vibes,
  onChange,
  onPresetSelect,
  queryText,
  onQueryChange,
  onSearch,
  loading,
  activeImage,
  imagePreviewUrl,
  onImageUpload,
  onClearImage
}) {
  const [showDetailedSliders, setShowDetailedSliders] = useState(false);

  const handleLevelSelect = (dimKey, level) => {
    onChange({
      ...vibes,
      [dimKey]: level,
    });
  };

  return (
    <div style={{
      background: '#ffffff',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid #e2e8f0',
      padding: '1.25rem 1.5rem',
      boxShadow: 'var(--shadow-sm)',
      marginBottom: '2.5rem'
    }}>
      {/* Search Input Bar inside Filter Card */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        marginBottom: '1.25rem',
        paddingBottom: '1.25rem',
        borderBottom: '1px solid #f1f5f9',
        flexWrap: 'wrap'
      }}>
        <div style={{
          position: 'relative',
          flex: 1,
          minWidth: '260px',
          display: 'flex',
          alignItems: 'center'
        }}>
          <Search
            size={18}
            style={{
              position: 'absolute',
              left: '1rem',
              color: '#64748b',
              pointerEvents: 'none'
            }}
          />
          <input
            type="text"
            className="input-field"
            placeholder="Search by keywords, tags, or places (e.g. 'pine trails', 'tea gardens', 'waterfalls', 'monasteries')..."
            style={{
              paddingLeft: '2.75rem',
              paddingRight: queryText ? '2.5rem' : '1rem',
              height: '46px',
              fontSize: '0.92rem',
              borderRadius: 'var(--radius-md)',
              border: '1.5px solid #cbd5e1',
              background: '#f8fafc'
            }}
            value={queryText || ''}
            onChange={(e) => onQueryChange(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onSearch()}
          />
          {queryText && (
            <button
              type="button"
              onClick={() => {
                onQueryChange('');
                setTimeout(() => onSearch(), 10);
              }}
              style={{
                position: 'absolute',
                right: '0.85rem',
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: '#94a3b8',
                display: 'flex',
                alignItems: 'center',
                padding: '4px'
              }}
              title="Clear search"
            >
              <X size={16} />
            </button>
          )}
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <label
            htmlFor="vibe-image-upload"
            className="btn btn-secondary"
            title="Upload an aesthetic photo (mountains, beaches, culture, cafes) to search by Deep Learning visual vibe!"
            style={{
              height: '46px',
              padding: '0 1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: 600,
              fontSize: '0.88rem',
              background: activeImage ? '#f0fdf4' : '#f8fafc',
              borderColor: activeImage ? '#86efac' : '#cbd5e1',
              color: activeImage ? '#166534' : '#334155'
            }}
          >
            <Camera size={18} color={activeImage ? '#16a34a' : '#475569'} />
            <span>{activeImage ? 'Photo Attached' : 'Photo Search'}</span>
            <input
              id="vibe-image-upload"
              type="file"
              accept="image/*"
              style={{ display: 'none' }}
              disabled={loading}
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  onImageUpload(e.target.files[0]);
                }
              }}
            />
          </label>

          <button
            type="button"
            className="btn btn-primary"
            onClick={onSearch}
            disabled={loading}
            style={{
              height: '46px',
              padding: '0 1.5rem',
              fontWeight: 700,
              whiteSpace: 'nowrap'
            }}
          >
            {loading ? 'Searching...' : 'Search Filters'}
          </button>
        </div>
      </div>

      {/* Active Photo Visual Search Banner */}
      {activeImage && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%)',
          border: '1.5px solid #86efac',
          borderRadius: 'var(--radius-md)',
          padding: '0.65rem 1rem',
          marginBottom: '1.25rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {imagePreviewUrl && (
              <img
                src={imagePreviewUrl}
                alt="Uploaded moodboard"
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '6px',
                  objectFit: 'cover',
                  border: '1px solid #bbf7d0',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                }}
              />
            )}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#166534' }}>
                  CLIP Visual Vibe Active:
                </span>
                <span style={{ fontSize: '0.82rem', color: '#15803d' }}>
                  {activeImage.name}
                </span>
              </div>
              <p style={{ margin: 0, fontSize: '0.75rem', color: '#16a34a' }}>
                Extracted visual aesthetic features using OpenAI CLIP ViT-B/32 & matched against all destinations.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClearImage}
            style={{
              background: '#ffffff',
              border: '1px solid #bbf7d0',
              borderRadius: '6px',
              padding: '0.3rem 0.6rem',
              fontSize: '0.78rem',
              color: '#dc2626',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem'
            }}
          >
            <X size={14} /> Remove Photo
          </button>
        </div>
      )}

      {/* Preset Travel Styles & Filter Toggle */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{
              background: '#f0f9ff',
              color: '#0284c7',
              padding: '0.2rem 0.55rem',
              borderRadius: '4px',
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.04em'
            }}>
              Curated Styles
            </span>
            <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a' }}>
              Filter by Travel Style
            </span>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '2px' }}>
            Choose curated travel themes or fine-tune specific environment preferences
          </p>
        </div>

        {/* Quick Style Presets */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
          {PRESETS.map((p) => (
            <button
              key={p.name}
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => onPresetSelect(p.vibes)}
              style={{ fontSize: '0.82rem', fontWeight: 600, padding: '0.4rem 0.85rem' }}
            >
              {p.name}
            </button>
          ))}

          <button
            type="button"
            className="btn btn-outline-primary btn-sm"
            onClick={() => setShowDetailedSliders(!showDetailedSliders)}
            style={{ fontSize: '0.82rem' }}
          >
            <SlidersHorizontal size={14} />
            {showDetailedSliders ? 'Hide Filters' : 'Fine-Tune Filters'}
            {showDetailedSliders ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        </div>
      </div>

      {/* Expandable 5 Preference Dimension Selectors */}
      {showDetailedSliders && (
        <div style={{
          marginTop: '1.25rem',
          paddingTop: '1.25rem',
          borderTop: '1px solid #f1f5f9',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
          gap: '1rem'
        }}>
          {VIBE_DIMS.map((dim) => {
            const Icon = dim.icon;
            const currentLevel = vibes[dim.key] || 'medium';

            return (
              <div key={dim.key} className="vibe-slider-card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem', marginBottom: '0.25rem' }}>
                  <Icon size={15} style={{ color: dim.color }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f172a' }}>{dim.label}</span>
                </div>
                <p style={{ fontSize: '0.74rem', color: '#64748b', minHeight: '30px' }}>{dim.desc}</p>

                <div className="vibe-radio-group">
                  <button
                    type="button"
                    className={`vibe-radio-btn ${currentLevel === 'low' ? 'active' : ''}`}
                    onClick={() => handleLevelSelect(dim.key, 'low')}
                  >
                    Low
                  </button>
                  <button
                    type="button"
                    className={`vibe-radio-btn ${currentLevel === 'medium' ? 'active' : ''}`}
                    onClick={() => handleLevelSelect(dim.key, 'medium')}
                  >
                    Med
                  </button>
                  <button
                    type="button"
                    className={`vibe-radio-btn ${currentLevel === 'high' ? 'active' : ''}`}
                    onClick={() => handleLevelSelect(dim.key, 'high')}
                  >
                    High
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
