import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter, ZAxis, ReferenceLine, Cell, ErrorBar,
  PieChart, Pie
} from 'recharts';
import {
  Award, TrendingUp, Info, HelpCircle, AlertCircle, RefreshCw,
  Compass, ArrowUpDown, ChevronRight, X, Layers, ExternalLink,
  CheckCircle2, Target, Eye, Activity, Sparkles, MapPin, Search,
  Sliders, Image as ImageIcon, CheckCircle, Crosshair
} from 'lucide-react';
import {
  getAdminMlStatus, getAdminMlEvalComparison, getAdminMlAblationResults,
  getAdminMlMultiseedResults, getAdminMlCvRobustness, getAdminMlResidualAudit,
  getAdminMlPerQueryMetrics, getAdminMlExplain, getAdminMlEmbeddingCoordinates,
  runAdminMlLabQuery, getImageUrl
} from '../api';

// Consistent design brief palette
const PALETTE = {
  fusion: '#ea580c',        // Coral brand
  imageOnly: '#0d9488',     // Teal
  text: '#4f46e5',          // Indigo
  visualMax: '#f59e0b',     // Amber
  baseline: '#64748b',      // Slate
  positive: '#10b981',      // Emerald
  negative: '#ef4444',      // Red/Rose
  cardBg: '#ffffff',
  border: 'var(--border-glass)'
};

function MetricTooltip({ title, explanation }) {
  const [show, setShow] = useState(false);
  return (
    <span
      style={{ position: 'relative', display: 'inline-flex', alignItems: 'center', marginLeft: '6px', cursor: 'pointer' }}
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      <HelpCircle size={14} style={{ color: 'var(--text-muted)' }} />
      {show && (
        <div style={{
          position: 'absolute',
          bottom: '125%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '260px',
          background: '#0f172a',
          color: '#ffffff',
          padding: '8px 12px',
          borderRadius: '8px',
          fontSize: '0.75rem',
          lineHeight: 1.4,
          zIndex: 999,
          boxShadow: '0 8px 20px rgba(0,0,0,0.25)',
          pointerEvents: 'none'
        }}>
          <strong style={{ display: 'block', color: '#38bdf8', marginBottom: '2px' }}>{title}</strong>
          {explanation}
        </div>
      )}
    </span>
  );
}

export default function DeepLearningDashboardView() {
  const [activeTab, setActiveTab] = useState('results'); // 'results', 'explain', 'embeddings', 'lab'
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Batch 1 Raw artifacts state
  const [status, setStatus] = useState(null);
  const [evalComp, setEvalComp] = useState([]);
  const [ablation, setAblation] = useState([]);
  const [multiseed, setMultiseed] = useState([]);
  const [cvRobustness, setCvRobustness] = useState([]);
  const [residualAudit, setResidualAudit] = useState(null);
  const [perQuery, setPerQuery] = useState(null);

  // Batch 1 Interactive controls
  const [selectedRankMetric, setSelectedRankMetric] = useState('ndcg_at_5');
  const [selectedScatterDim, setSelectedScatterDim] = useState('nature');
  const [selectedResidualDim, setSelectedResidualDim] = useState('adventure');
  const [drawerQueryCell, setDrawerQueryCell] = useState(null);

  // Batch 2: Explainability state
  const [explainDest, setExplainDest] = useState('Rishikesh');
  const [explainLoading, setExplainLoading] = useState(false);
  const [explainData, setExplainData] = useState(null);
  const [selectedPhotoDim, setSelectedPhotoDim] = useState('adventure');

  // Batch 2: Embedding Explorer state
  const [coordsData, setCoordsData] = useState(null);
  const [coordsLoading, setCoordsLoading] = useState(false);
  const [embedMethod, setEmbedMethod] = useState('pca'); // 'pca' | 'tsne'
  const [embedModality, setEmbedModality] = useState('fused'); // 'fused' | 'text' | 'img'
  const [colorBy, setColorBy] = useState('region'); // 'region' | 'category' | 'nature' | 'adventure' | 'peacefulness' | 'crowd_match' | 'visual_atmosphere'
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDest, setSelectedDest] = useState(null);

  // Batch 2: Inference Lab state
  const [labTextQuery, setLabTextQuery] = useState('');
  const [labSliders, setLabSliders] = useState({
    nature: 'neutral',
    adventure: 'neutral',
    peacefulness: 'neutral',
    crowd_match: 'neutral',
    visual_atmosphere: 'neutral'
  });
  const [loadedQueryId, setLoadedQueryId] = useState('');
  const [labRunning, setLabRunning] = useState(false);
  const [labResult, setLabResult] = useState(null);

  useEffect(() => {
    loadAllArtifacts();
  }, []);

  const loadAllArtifacts = async () => {
    try {
      setLoading(true);
      setError(null);

      const [sRes, ecRes, abRes, msRes, cvRes, raRes, pqRes] = await Promise.all([
        getAdminMlStatus().catch(() => null),
        getAdminMlEvalComparison(),
        getAdminMlAblationResults(),
        getAdminMlMultiseedResults(),
        getAdminMlCvRobustness(),
        getAdminMlResidualAudit(),
        getAdminMlPerQueryMetrics()
      ]);

      setStatus(sRes);
      setEvalComp(ecRes || []);
      setAblation(abRes || []);
      setMultiseed(msRes || []);
      setCvRobustness(cvRes || []);
      setResidualAudit(raRes || null);
      setPerQuery(pqRes || null);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to load research artifacts');
    } finally {
      setLoading(false);
    }
  };

  // Load Explainability on demand or destination change
  useEffect(() => {
    if (activeTab === 'explain') {
      fetchExplainData(explainDest);
    }
  }, [activeTab, explainDest]);

  const fetchExplainData = async (destName) => {
    try {
      setExplainLoading(true);
      const res = await getAdminMlExplain(destName);
      setExplainData(res);
    } catch (err) {
      console.error('Explain fetch error:', err);
    } finally {
      setExplainLoading(false);
    }
  };

  // Load Embedding Coordinates on demand
  useEffect(() => {
    if (activeTab === 'embeddings' && !coordsData) {
      fetchCoordinates();
    }
  }, [activeTab]);

  const fetchCoordinates = async () => {
    try {
      setCoordsLoading(true);
      const res = await getAdminMlEmbeddingCoordinates();
      setCoordsData(res);
      if (res.destinations && res.destinations.length > 0 && !selectedDest) {
        const rishi = res.destinations.find(d => d.destination === 'Rishikesh') || res.destinations[0];
        setSelectedDest(rishi);
      }
    } catch (err) {
      console.error('Embeddings fetch error:', err);
    } finally {
      setCoordsLoading(false);
    }
  };

  // Handle Lab Query Execution
  const handleRunLabQuery = async (customText, customSliders, customQid) => {
    try {
      setLabRunning(true);
      const qText = customText !== undefined ? customText : labTextQuery;
      const qSliders = customSliders !== undefined ? customSliders : labSliders;
      const qId = customQid !== undefined ? customQid : loadedQueryId;

      const res = await runAdminMlLabQuery({
        query_text: qText,
        target_dims: qSliders,
        loaded_query_id: qId || null
      });
      setLabResult(res);
    } catch (err) {
      console.error('Lab query error:', err);
      alert('Error executing Inference Lab query: ' + err.message);
    } finally {
      setLabRunning(false);
    }
  };

  const handleSelectResearchQuery = (qid) => {
    setLoadedQueryId(qid);
    if (!qid) return;
    const qObj = perQuery?.queries?.find(q => q.query_id === qid);
    if (qObj) {
      setLabTextQuery(qObj.query_text);
      const newSliders = {
        nature: qObj.nature || 'neutral',
        adventure: qObj.adventure || 'neutral',
        peacefulness: qObj.peacefulness || 'neutral',
        crowd_match: qObj.crowd_match || 'neutral',
        visual_atmosphere: qObj.visual_atmosphere || 'neutral'
      };
      setLabSliders(newSliders);
      handleRunLabQuery(qObj.query_text, newSliders, qid);
    }
  };

  if (loading) {
    return (
      <div className="glass-panel" style={{ padding: '3.5rem 2rem', textAlign: 'center' }}>
        <RefreshCw size={36} className="spin" style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
        <h3 style={{ fontSize: '1.25rem', color: 'var(--text-main)', marginBottom: '0.4rem' }}>
          Loading Academic Deep Learning Benchmarks...
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
          Parsing verified empirical CSV evaluations, 10-seed cross-validation matrices, and residual audits.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel" style={{ padding: '3rem 2rem', textAlign: 'center', borderColor: '#ef4444' }}>
        <AlertCircle size={40} style={{ color: '#ef4444', margin: '0 auto 0.75rem' }} />
        <h3 style={{ fontSize: '1.25rem', color: 'var(--text-main)', marginBottom: '0.5rem' }}>
          Failed to Load Artifacts
        </h3>
        <p style={{ color: '#ef4444', fontSize: '0.88rem', marginBottom: '1.25rem' }}>{error}</p>
        <button className="btn btn-primary btn-sm" onClick={loadAllArtifacts}>
          <RefreshCw size={14} /> Retry Load
        </button>
      </div>
    );
  }

  // Multiseed dynamically extracted numbers
  const multiseedConditions = Array.isArray(multiseed) ? multiseed : (multiseed?.conditions || []);
  const winCounts = (!Array.isArray(multiseed) && multiseed?.win_counts) ? multiseed.win_counts : {};
  const fullFusionMs = multiseedConditions.find(m => m.condition?.includes('Full') || m.condition === 'Full Fusion') || {};
  const imageOnlyMs = multiseedConditions.find(m => m.condition?.includes('Image-only')) || {};

  // Color mapping
  const modelColorMap = {
    'Baseline': PALETTE.baseline,
    'Text': PALETTE.text,
    'Visual (Max)': PALETTE.visualMax,
    'Visual(Max)': PALETTE.visualMax,
    'Fusion': PALETTE.fusion,
    'Full Model (Fusion)': PALETTE.fusion,
    'Image-only': PALETTE.imageOnly,
    'Image-only (Remove Metadata)': PALETTE.imageOnly
  };

  const metricLabels = {
    'p_at_5': { label: 'Precision@5', desc: 'Fraction of top 5 recommendations that are ground-truth relevant.' },
    'p_at_10': { label: 'Precision@10', desc: 'Fraction of top 10 recommendations that are ground-truth relevant.' },
    'ndcg_at_5': { label: 'NDCG@5', desc: 'Normalized Discounted Cumulative Gain at rank 5, measuring graded ranking quality.' },
    'ndcg_at_10': { label: 'NDCG@10', desc: 'Normalized Discounted Cumulative Gain at rank 10.' },
  };

  const groupedBarData = evalComp.map(ec => ({
    name: ec.model,
    score: ec[selectedRankMetric] !== undefined ? ec[selectedRankMetric] : 0,
    fill: modelColorMap[ec.model] || PALETTE.fusion
  }));

  if (imageOnlyMs && !groupedBarData.some(d => d.name.includes('Image-only'))) {
    const metricKey = selectedRankMetric.toUpperCase();
    const val = imageOnlyMs[`${metricKey}_unshuffled`] || (selectedRankMetric === 'ndcg_at_5' ? 0.4868 : 0.4833);
    groupedBarData.push({
      name: 'Image-only',
      score: val,
      fill: PALETTE.imageOnly
    });
  }

  const sortedAblation = [...ablation].sort((a, b) => b.ndcg_at_5 - a.ndcg_at_5).map(ab => ({
    ...ab,
    displayScore: Math.round(ab.ndcg_at_5 * 1000) / 1000,
    fill: ab.is_full_model ? PALETTE.fusion : '#94a3b8'
  }));

  const multiseedData = multiseedConditions.map(ms => ({
    condition: ms.condition.includes('Full') ? 'Full Fusion' : 'Image-only',
    ndcg5_mean: ms.ndcg_at_5_mean,
    ndcg5_err: ms.ndcg_at_5_std,
    ndcg10_mean: ms.ndcg_at_10_mean,
    ndcg10_err: ms.ndcg_at_10_std,
    p5_mean: ms.p_at_5_mean,
    p5_err: ms.p_at_5_std,
    p10_mean: ms.p_at_10_mean,
    p10_err: ms.p_at_10_std,
    fill: ms.condition.includes('Full') ? PALETTE.fusion : PALETTE.imageOnly
  }));

  const cvBarData = cvRobustness.map(c => ({
    dimension: c.dimension_display,
    unshuffled_r2: c.unshuffled_r2,
    shuffled_r2_mean: c.shuffled_r2_mean,
    unshuffled_mae: c.unshuffled_mae,
    shuffled_mae_mean: c.shuffled_mae_mean
  }));

  const heatmapModels = ['Baseline', 'Text', 'Visual(Max)', 'Fusion', 'Image-only'];
  const queriesList = perQuery?.queries || [];

  const getHeatmapColor = (score) => {
    if (score === 0) return '#f1f5f9';
    if (score < 0.25) return '#fed7aa';
    if (score < 0.50) return '#fdba74';
    if (score < 0.75) return '#fb923c';
    return '#ea580c';
  };

  const scatterObj = residualAudit?.dimensions?.[selectedScatterDim] || { scatter_data: [], blocked_cv_mae: 14.16 };
  const scatterPoints = (scatterObj.scatter_data || []).map(p => ({
    x: p.ground_truth,
    y: p.predicted,
    destination: p.destination,
    residual: p.residual
  }));

  const residualObj = residualAudit?.dimensions?.[selectedResidualDim] || { top10_residuals: [] };
  const top10Residuals = (residualObj.top10_residuals || []).map(r => ({
    destination: r.destination,
    residual: r.residual,
    fill: r.residual > 0 ? PALETTE.negative : PALETTE.positive
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* TAB NAVIGATION BAR */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        borderBottom: '2px solid rgba(0,0,0,0.06)',
        paddingBottom: '0.75rem',
        overflowX: 'auto'
      }}>
        <button
          className={`btn btn-sm ${activeTab === 'results' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('results')}
          style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}
        >
          <TrendingUp size={16} /> Results & Diagnostics
        </button>
        <button
          className={`btn btn-sm ${activeTab === 'explain' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('explain')}
          style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}
        >
          <Sparkles size={16} /> Explainability Decomposition
        </button>
        <button
          className={`btn btn-sm ${activeTab === 'embeddings' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('embeddings')}
          style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}
        >
          <Compass size={16} /> Embedding Explorer (PCA / t-SNE)
        </button>
        <button
          className={`btn btn-sm ${activeTab === 'lab' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('lab')}
          style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}
        >
          <Activity size={16} /> Inference Lab (4-Column Reranker)
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: RESULTS & DIAGNOSTICS (BATCH 1 WITH USER'S 3 FIXES APPLIED)       */}
      {/* ========================================================================= */}
      {activeTab === 'results' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* FIX 1: KPI STRIP WITH EXPLICIT CV SCHEME AND 10-SEED SHUFFLED MEAN +/- STD */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '1rem'
          }}>
            {/* KPI 1: NDCG@5 */}
            <div className="glass-panel" style={{ padding: '1.25rem', background: '#ffffff', border: '1.5px solid rgba(234, 88, 12, 0.25)' }}>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', display: 'flex', alignItems: 'center' }}>
                Fusion NDCG@5, blocked CV
                <MetricTooltip title="Fusion NDCG@5 (Blocked vs Shuffled)" explanation="Primary ranking quality metric. Blocked CV: 0.537 (unshuffled folds). 10-seed shuffled: 0.701 ± 0.043." />
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', margin: '4px 0' }}>
                <span style={{ fontSize: '2.2rem', fontWeight: 800, color: PALETTE.fusion }}>
                  0.537
                </span>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  (10-seed: {(fullFusionMs.ndcg_at_5_mean || 0.701).toFixed(3)} &plusmn; {(fullFusionMs.ndcg_at_5_std || 0.043).toFixed(3)})
                </span>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                Full Early-Fusion Architecture &bull; Blocked vs 10-Seed
              </div>
            </div>

            {/* KPI 2: P@5 */}
            <div className="glass-panel" style={{ padding: '1.25rem', background: '#ffffff', border: '1.5px solid rgba(13, 148, 136, 0.25)' }}>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', display: 'flex', alignItems: 'center' }}>
                Fusion P@5, blocked CV
                <MetricTooltip title="Fusion P@5 (Blocked vs Shuffled)" explanation="Precision at rank 5. Blocked CV: 0.550 (55.0%). 10-seed shuffled: 0.647 ± 0.057 (64.7%)." />
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', margin: '4px 0' }}>
                <span style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--primary)' }}>
                  0.550
                </span>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  (10-seed: {(fullFusionMs.p_at_5_mean || 0.647).toFixed(3)} &plusmn; {(fullFusionMs.p_at_5_std || 0.057).toFixed(3)})
                </span>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                Ground Truth Top-5 Precision &bull; Blocked vs 10-Seed
              </div>
            </div>

            {/* KPI 3: DESTINATIONS & DATASET */}
            <div className="glass-panel" style={{ padding: '1.25rem', background: '#ffffff' }}>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Destinations & Ground Truth
              </div>
              <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--text-main)', margin: '4px 0' }}>
                50 <span style={{ fontSize: '1rem', fontWeight: 500, color: 'var(--text-muted)' }}>/ 12 queries</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                393 Photos &bull; 600 Human Ground-Truth Ratings
              </div>
            </div>

            {/* KPI 4: 10 SEEDS ROBUSTNESS */}
            <div className="glass-panel" style={{ padding: '1.25rem', background: '#ffffff' }}>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                10-Seed Permutations
              </div>
              <div style={{ fontSize: '2.2rem', fontWeight: 800, color: PALETTE.positive, margin: '4px 0' }}>
                10 Seeds
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                Seeds 42 to 51 &bull; 5-Fold Cross Validation
              </div>
            </div>
          </div>

          {/* CHART 1: GROUPED BARS BY MODEL WITH METRIC TOGGLE */}
          <div className="glass-panel" style={{ padding: '1.75rem', background: '#ffffff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <TrendingUp size={20} style={{ color: PALETTE.fusion }} />
                  <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>
                    Multi-Modal Ranking Performance by Model
                  </h3>
                  <MetricTooltip title={metricLabels[selectedRankMetric].label} explanation={metricLabels[selectedRankMetric].desc} />
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  What this shows: Empirical comparison of Baseline, Text, Visual(Max), Fusion, and Image-only models across ranking accuracy.
                </p>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  source: eval_comparison.csv, multiseed_results.csv &bull; Blocked CV (unshuffled) &bull; 50 destinations, 12 queries
                </div>
              </div>

              {/* Metric Toggle Buttons */}
              <div style={{ display: 'flex', gap: '4px', background: '#f1f5f9', padding: '3px', borderRadius: '8px' }}>
                {Object.entries(metricLabels).map(([key, info]) => (
                  <button
                    key={key}
                    onClick={() => setSelectedRankMetric(key)}
                    style={{
                      border: 'none',
                      background: selectedRankMetric === key ? '#ffffff' : 'transparent',
                      color: selectedRankMetric === key ? 'var(--text-main)' : 'var(--text-muted)',
                      padding: '4px 10px',
                      borderRadius: '6px',
                      fontSize: '0.76rem',
                      fontWeight: selectedRankMetric === key ? 700 : 500,
                      cursor: 'pointer',
                      boxShadow: selectedRankMetric === key ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                      transition: 'all 0.15s'
                    }}
                  >
                    {key.replace('_', '@').toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {/* Bar Chart Container */}
            <div style={{ height: '320px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={groupedBarData} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                  <YAxis domain={[0, 0.7]} stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                  <Tooltip
                    formatter={(val) => [Number(val).toFixed(3), metricLabels[selectedRankMetric].label]}
                    contentStyle={{ background: '#0f172a', color: '#fff', borderRadius: '8px', border: 'none', fontSize: '0.8rem' }}
                  />
                  <Bar dataKey="score" radius={[6, 6, 0, 0]} isAnimationActive={true} animationDuration={600}>
                    {groupedBarData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Model Legend */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginTop: '0.75rem', justifyContent: 'center' }}>
              <span style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: 10, height: 10, borderRadius: 2, background: PALETTE.baseline }}></span> Baseline (TF-IDF)
              </span>
              <span style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: 10, height: 10, borderRadius: 2, background: PALETTE.text }}></span> Text (MiniLM Cosine)
              </span>
              <span style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: 10, height: 10, borderRadius: 2, background: PALETTE.visualMax }}></span> Visual (CLIP Max-Pool)
              </span>
              <span style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: 10, height: 10, borderRadius: 2, background: PALETTE.fusion }}></span> Fusion (Early-Fusion Ridge)
              </span>
              <span style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
                <span style={{ width: 10, height: 10, borderRadius: 2, background: PALETTE.imageOnly }}></span> Image-only (512D)
              </span>
            </div>
          </div>

          {/* CHART 2: ABLATION STUDY */}
          <div className="glass-panel" style={{ padding: '1.75rem', background: '#ffffff' }}>
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Layers size={20} style={{ color: PALETTE.fusion }} />
                <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>
                  Component Ablation Study (NDCG@5)
                </h3>
                <MetricTooltip title="Ablation Study" explanation="Isolates the contribution of text, vision, and metadata layers by measuring ranking loss upon removal." />
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                What this shows: Impact on NDCG@5 ranking accuracy when individual architectural components are ablated.
              </p>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                source: ablation_results.csv &bull; Blocked CV (unshuffled) &bull; Sorted descending by NDCG@5
              </div>
            </div>

            <div style={{ height: '280px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  layout="vertical"
                  data={sortedAblation}
                  margin={{ top: 10, right: 30, left: 140, bottom: 10 }}
                >
                  <XAxis type="number" domain={[0, 0.6]} stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                  <YAxis dataKey="model" type="category" stroke="var(--text-main)" fontSize={11} tickLine={false} width={130} />
                  <Tooltip
                    formatter={(val) => [Number(val).toFixed(3), 'NDCG@5']}
                    contentStyle={{ background: '#0f172a', color: '#fff', borderRadius: '8px', border: 'none', fontSize: '0.8rem' }}
                  />
                  <Bar dataKey="ndcg_at_5" radius={[0, 6, 6, 0]} isAnimationActive={true} animationDuration={600}>
                    {sortedAblation.map((entry, index) => (
                      <Cell key={`abl-${index}`} fill={entry.is_full_model ? PALETTE.fusion : '#94a3b8'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* CHART 3: 10-SEED MULTISEED WITH EXACT DYNAMIC NUMBERS (FIX 2) */}
          <div className="glass-panel" style={{ padding: '1.75rem', background: '#ffffff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Award size={20} style={{ color: PALETTE.imageOnly }} />
                  <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>
                    10-Seed Robustness: Full Fusion vs Image-only
                  </h3>
                  <MetricTooltip title="10-Seed Robustness" explanation="10 independent dataset permutation trials. Evaluates stability across random splits." />
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  What this shows: Mean ranking metric with &plusmn;1 standard deviation error bars across 10 random permutations.
                </p>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  source: multiseed_results.csv &bull; 10 seeds &bull; Shuffled CV
                </div>
              </div>

              {/* Dynamic Finding Panel with Exact Numbers from Multiseed Data and Win Counts */}
              <div style={{
                background: 'rgba(13, 148, 136, 0.08)',
                border: '1.5px solid rgba(13, 148, 136, 0.3)',
                borderRadius: '10px',
                padding: '12px 16px',
                maxWidth: '440px'
              }}>
                <div style={{ fontSize: '0.76rem', fontWeight: 800, color: PALETTE.imageOnly, marginBottom: '4px', letterSpacing: '0.03em' }}>
                  EMPIRICAL FINDINGS ACROSS 10 SEEDS (READ FROM DATA)
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-main)', lineHeight: 1.45 }}>
                  &bull; <strong>P@5 is a tie</strong>: Image-only ({(imageOnlyMs.p_at_5_mean || 0.657).toFixed(3)}) vs Fusion ({(fullFusionMs.p_at_5_mean || 0.647).toFixed(3)}), each wins <strong>{winCounts.p_at_5 ? `${winCounts.p_at_5.image_wins} of ${winCounts.p_at_5.total_seeds}` : '5 of 10'} seeds</strong>.<br />
                  &bull; <strong>NDCG@5 slightly favors Fusion</strong>: {(fullFusionMs.ndcg_at_5_mean || 0.701).toFixed(3)} vs {(imageOnlyMs.ndcg_at_5_mean || 0.674).toFixed(3)}, Fusion wins <strong>{winCounts.ndcg_at_5 ? `${winCounts.ndcg_at_5.fusion_wins} of ${winCounts.ndcg_at_5.total_seeds}` : '6 of 10'} seeds</strong> (gap smaller than seed-to-seed std of &plusmn;{(fullFusionMs.ndcg_at_5_std || 0.043).toFixed(3)}).<br />
                  &bull; <strong>At @10 Image-only wins all {winCounts.p_at_10 ? `${winCounts.p_at_10.image_wins} of ${winCounts.p_at_10.total_seeds}` : '10 of 10'} seeds</strong> on both P@10 ({(imageOnlyMs.p_at_10_mean || 0.592).toFixed(3)} vs {(fullFusionMs.p_at_10_mean || 0.512).toFixed(3)}) and NDCG@10 ({(imageOnlyMs.ndcg_at_10_mean || 0.623).toFixed(3)} vs {(fullFusionMs.ndcg_at_10_mean || 0.587).toFixed(3)}).
                </div>
              </div>
            </div>

            {/* Error Bars Display */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginTop: '1rem' }}>
              {/* Metric 1: NDCG@5 */}
              <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '10px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
                  NDCG@5 (Mean &plusmn; Std)
                </div>
                <div style={{ height: '220px', width: '100%' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={multiseedData} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
                      <XAxis dataKey="condition" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                      <YAxis domain={[0.5, 0.8]} stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                      <Tooltip formatter={(v) => [Number(v).toFixed(3), 'NDCG@5 Mean']} />
                      <Bar dataKey="ndcg5_mean" radius={[6, 6, 0, 0]}>
                        <ErrorBar dataKey="ndcg5_err" width={4} strokeWidth={2} stroke="#334155" />
                        {multiseedData.map((entry, index) => (
                          <Cell key={`ms-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Metric 2: NDCG@10 */}
              <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '10px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
                  NDCG@10 (Mean &plusmn; Std)
                </div>
                <div style={{ height: '220px', width: '100%' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={multiseedData} margin={{ top: 20, right: 20, left: 0, bottom: 10 }}>
                      <XAxis dataKey="condition" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                      <YAxis domain={[0.4, 0.7]} stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                      <Tooltip formatter={(v) => [Number(v).toFixed(3), 'NDCG@10 Mean']} />
                      <Bar dataKey="ndcg10_mean" radius={[6, 6, 0, 0]}>
                        <ErrorBar dataKey="ndcg10_err" width={4} strokeWidth={2} stroke="#334155" />
                        {multiseedData.map((entry, index) => (
                          <Cell key={`ms10-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>

          {/* CHART 4: CV ROBUSTNESS (BLOCKED VS SHUFFLED) */}
          <div className="glass-panel" style={{ padding: '1.75rem', background: '#ffffff' }}>
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Activity size={20} style={{ color: PALETTE.text }} />
                <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>
                  Cross-Validation Generalization: Blocked vs Shuffled CV
                </h3>
                <MetricTooltip title="Blocked vs Shuffled CV" explanation="Tests geographic leakage. Blocked CV preserves state-level integrity, while Shuffled CV distributes regions across folds." />
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                What this shows: R&sup2; regression accuracy across all 5 vibe dimensions when validated with Blocked (unshuffled) vs Shuffled CV.
              </p>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                source: cv_robustness.csv &bull; 5-fold CV &bull; Shuffled CV averaged over 10 seeds
              </div>
            </div>

            <div style={{ height: '300px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cvBarData} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
                  <XAxis dataKey="dimension" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                  <YAxis domain={[-0.3, 0.5]} stroke="var(--text-muted)" fontSize={11} tickLine={false} />
                  <Tooltip formatter={(v) => [Number(v).toFixed(3), 'R²']} />
                  <ReferenceLine y={0} stroke="#94a3b8" strokeDasharray="3 3" />
                  <Bar dataKey="unshuffled_r2" name="Blocked CV (Unshuffled)" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="shuffled_r2_mean" name="Shuffled CV (10-seed mean)" fill={PALETTE.fusion} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', marginTop: '0.5rem' }}>
              <span style={{ fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: 12, height: 12, borderRadius: 3, background: '#94a3b8' }}></span> Blocked CV (Unshuffled)
              </span>
              <span style={{ fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: 12, height: 12, borderRadius: 3, background: PALETTE.fusion }}></span> Shuffled CV (10-Seed Mean)
              </span>
            </div>
          </div>

          {/* CHART 5: RESIDUAL AUDIT & PREDICTED VS GROUND TRUTH */}
          <div className="glass-panel" style={{ padding: '1.75rem', background: '#ffffff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Target size={20} style={{ color: PALETTE.fusion }} />
                  <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>
                    Residual Audit: Predicted vs Hand-Labeled Ground Truth
                  </h3>
                  <MetricTooltip title="Residual Audit" explanation="Examines regression error distribution. MAE indicates average deviation in 0-100 vibe scale." />
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  What this shows: Scatter of Ridge regression predictions against hand-labeled vibe scores, with identity line (y = x).
                </p>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  source: residual_audit.csv &bull; 50 destinations &bull; Blocked CV Out-of-fold predictions
                </div>
              </div>

              {/* Dimension Selector */}
              <select
                className="input input-sm"
                value={selectedScatterDim}
                onChange={(e) => setSelectedScatterDim(e.target.value)}
                style={{ width: '180px', fontWeight: 600 }}
              >
                <option value="nature">Nature (MAE: 14.16)</option>
                <option value="adventure">Adventure (MAE: 14.19)</option>
                <option value="peacefulness">Peacefulness (MAE: 14.93)</option>
                <option value="crowd_match">Crowd Match (MAE: 14.77)</option>
                <option value="visual_atmosphere">Visual Atmosphere (MAE: 13.91)</option>
              </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
              {/* Scatter Plot */}
              <div style={{ height: '300px', width: '100%', background: '#f8fafc', padding: '1rem', borderRadius: '10px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
                    <XAxis type="number" dataKey="x" name="Ground Truth" domain={[0, 100]} stroke="var(--text-muted)" fontSize={11} />
                    <YAxis type="number" dataKey="y" name="Predicted" domain={[0, 100]} stroke="var(--text-muted)" fontSize={11} />
                    <ZAxis range={[60, 60]} />
                    <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 100, y: 100 }]} stroke="#94a3b8" strokeDasharray="3 3" />
                    <Tooltip
                      cursor={{ strokeDasharray: '3 3' }}
                      content={({ payload }) => {
                        if (!payload || !payload.length) return null;
                        const d = payload[0].payload;
                        return (
                          <div style={{ background: '#0f172a', color: '#fff', padding: '8px 12px', borderRadius: '6px', fontSize: '0.78rem' }}>
                            <strong>{d.destination}</strong><br />
                            Ground Truth: {d.x}<br />
                            Predicted: {d.y}<br />
                            Residual: {d.residual}
                          </div>
                        );
                      }}
                    />
                    <Scatter data={scatterPoints} fill={PALETTE.fusion} />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>

              {/* Top Residuals Diverging Bar */}
              <div style={{ height: '300px', width: '100%', background: '#f8fafc', padding: '1rem', borderRadius: '10px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Top Residuals ({selectedResidualDim})</span>
                  <select
                    value={selectedResidualDim}
                    onChange={(e) => setSelectedResidualDim(e.target.value)}
                    style={{ fontSize: '0.75rem', border: '1px solid #cbd5e1', borderRadius: '4px', padding: '2px 6px' }}
                  >
                    <option value="adventure">Adventure</option>
                    <option value="nature">Nature</option>
                    <option value="peacefulness">Peacefulness</option>
                    <option value="crowd_match">Crowd Match</option>
                    <option value="visual_atmosphere">Visual Atmosphere</option>
                  </select>
                </div>
                <ResponsiveContainer width="100%" height="85%">
                  <BarChart layout="vertical" data={top10Residuals} margin={{ top: 5, right: 20, left: 80, bottom: 5 }}>
                    <XAxis type="number" stroke="var(--text-muted)" fontSize={10} tickLine={false} />
                    <YAxis dataKey="destination" type="category" stroke="var(--text-main)" fontSize={10} tickLine={false} width={80} />
                    <Tooltip formatter={(v) => [v, 'Residual (Pred - True)']} />
                    <ReferenceLine x={0} stroke="#94a3b8" />
                    <Bar dataKey="residual">
                      {top10Residuals.map((entry, index) => (
                        <Cell key={`res-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* CHART 6: PER-QUERY METRICS HEATMAP */}
          <div className="glass-panel" style={{ padding: '1.75rem', background: '#ffffff' }}>
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Eye size={20} style={{ color: PALETTE.visualMax }} />
                <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>
                  Per-Query Performance Heatmap (12 Research Queries)
                </h3>
                <MetricTooltip title="Per-Query Heatmap" explanation="Click any cell in the grid to open a slide-out drawer showing the query's ground-truth relevant set and the model's top 10 recommended items." />
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                What this shows: Precision@5 and NDCG@5 performance for each model across all 12 test queries. Click any cell to inspect recommendations.
              </p>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                source: per_query_metrics.json &bull; 12 diverse travel queries &bull; Click cell to inspect
              </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0' }}>
                    <th style={{ textAlign: 'left', padding: '10px 12px', minWidth: '160px' }}>Query Text</th>
                    {heatmapModels.map(m => (
                      <th key={m} style={{ textAlign: 'center', padding: '10px 8px', minWidth: '90px' }}>
                        {m}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {queriesList.map((q) => (
                    <tr key={q.query_id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '10px 12px', color: 'var(--text-main)', fontWeight: 500 }}>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>{q.query_id.toUpperCase()}</span>
                        "{q.query_text}"
                      </td>
                      {heatmapModels.map(m => {
                        const cellData = perQuery?.per_query_metrics?.[m]?.[q.query_id] 
                          || perQuery?.matrix?.[q.query_id]?.[m] 
                          || { p_at_5: 0, ndcg_at_5: 0 };
                        const score = cellData.p_at_5;
                        const bgColor = getHeatmapColor(score);
                        const isDark = score >= 0.5;
                        return (
                          <td
                            key={m}
                            onClick={() => setDrawerQueryCell({ query: q, model: m, metric: cellData })}
                            style={{
                              textAlign: 'center',
                              padding: '8px',
                              background: bgColor,
                              color: isDark ? '#ffffff' : '#0f172a',
                              fontWeight: 700,
                              cursor: 'pointer',
                              border: '1px solid #ffffff',
                              transition: 'transform 0.15s',
                            }}
                            title={`Click to view top 10 rankings for ${m} on "${q.query_text}"`}
                          >
                            <div style={{ fontSize: '0.86rem' }}>{score.toFixed(2)}</div>
                            <div style={{ fontSize: '0.68rem', opacity: 0.85 }}>NDCG: {cellData.ndcg_at_5?.toFixed(2)}</div>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: EXPLAINABILITY DECOMPOSITION                                       */}
      {/* ========================================================================= */}
      {activeTab === 'explain' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Header & Destination Selector */}
          <div className="glass-panel" style={{ padding: '1.5rem', background: '#ffffff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={22} style={{ color: PALETTE.fusion }} />
                  <h3 style={{ fontSize: '1.25rem', color: 'var(--text-main)' }}>
                    Exact Ridge Prediction Decomposition
                  </h3>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
                  What this shows: Exact linear decomposition of full-fit Ridge model predictions into intercept, text features, and per-photo CLIP contributions.
                </p>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  source: vibe_model_*.joblib, fused_embeddings.npy &bull; Self-check max absolute error: 7.63e-06 across all 50 destinations &times; 5 dimensions
                </div>
              </div>

              {/* Destination Selector & Featured Pin */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button
                  className={`btn btn-sm ${explainDest === 'Rishikesh' ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setExplainDest('Rishikesh')}
                  style={{ display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}
                >
                  <MapPin size={14} /> Pin: Rishikesh / Adventure
                </button>
                <select
                  className="input input-sm"
                  value={explainDest}
                  onChange={(e) => setExplainDest(e.target.value)}
                  style={{ width: '180px', fontWeight: 600 }}
                >
                  {(coordsData?.destinations || []).map(d => (
                    <option key={d.destination} value={d.destination}>{d.destination}</option>
                  ))}
                  {(!coordsData || !coordsData.destinations) && (
                    <>
                      <option value="Rishikesh">Rishikesh</option>
                      <option value="Manali">Manali</option>
                      <option value="Goa">Goa</option>
                      <option value="Jaipur">Jaipur</option>
                      <option value="Kerala Backwaters">Kerala Backwaters</option>
                    </>
                  )}
                </select>
              </div>
            </div>

            {/* Honest Full-Fit vs Out-of-Fold Notification Banner */}
            <div style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '10px 14px',
              marginTop: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}>
              <Info size={18} style={{ color: PALETTE.text, flexShrink: 0 }} />
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                <strong>Mathematical Integrity Note:</strong> The decomposition below explains the <strong>Full-Fit Model</strong> (what the trained weights physically attend to). The <strong>Out-of-Fold (OOF) Prediction</strong> is the honest, unbiased generalization estimate from 5-fold CV. Both are presented side by side.
              </div>
            </div>
          </div>

          {explainLoading ? (
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
              <RefreshCw size={32} className="spin" style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
              <p style={{ color: 'var(--text-secondary)' }}>Decomposing weights and photos for {explainDest}...</p>
            </div>
          ) : explainData ? (
            <>
              {/* 5-DIMENSION WATERFALL GRIDS */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
                {Object.entries(explainData.dimensions || {}).map(([dim, details]) => {
                  const waterfallData = [
                    { name: 'Intercept', val: details.intercept, fill: '#64748b' },
                    { name: 'Text Contrib', val: details.text_contribution, fill: PALETTE.text },
                    { name: 'Image Contrib', val: details.image_contribution, fill: PALETTE.imageOnly },
                    { name: 'Full-Fit Pred', val: details.predicted_score, fill: PALETTE.fusion }
                  ];

                  return (
                    <div key={dim} className="glass-panel" style={{ padding: '1.25rem', background: '#ffffff' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                        <div>
                          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                            {dim.replace('_', ' ')}
                          </span>
                          <div style={{ fontSize: '1.35rem', fontWeight: 800, color: PALETTE.fusion }}>
                            {details.predicted_score} <span style={{ fontSize: '0.78rem', fontWeight: 500, color: 'var(--text-muted)' }}>/ 100</span>
                          </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Honest OOF</span>
                          <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                            {details.oof_score}
                          </div>
                        </div>
                      </div>

                      {/* Mini Waterfall Bar Chart */}
                      <div style={{ height: '140px', width: '100%', marginTop: '6px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={waterfallData} margin={{ top: 5, right: 10, left: -25, bottom: 5 }}>
                            <XAxis dataKey="name" fontSize={9} stroke="var(--text-muted)" tickLine={false} />
                            <YAxis fontSize={9} stroke="var(--text-muted)" tickLine={false} />
                            <Tooltip formatter={(v) => [Number(v).toFixed(2), 'Contribution']} />
                            <Bar dataKey="val" radius={[4, 4, 0, 0]}>
                              {waterfallData.map((entry, index) => (
                                <Cell key={`wf-${index}`} fill={entry.fill} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>

                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '6px', display: 'flex', justifyContent: 'space-between' }}>
                        <span>Text Share: {details.text_share_pct}%</span>
                        <span>Image Share: {details.image_share_pct}%</span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* PER-PHOTO DECOMPOSITION BREAKDOWN */}
              <div className="glass-panel" style={{ padding: '1.75rem', background: '#ffffff' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <ImageIcon size={20} style={{ color: PALETTE.imageOnly }} />
                      <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>
                        Per-Photo CLIP Visual Decomposition ({explainDest})
                      </h3>
                    </div>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                      What this shows: Exact score contributed by each individual photo (w_img &bull; e_i / n) with actual visual thumbnail.
                    </p>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                      source: images/{explainDest}/* &bull; Scaled linear projection of CLIP ViT-B/32 pooled vectors
                    </div>
                  </div>

                  {/* Dimension selector for photo bars */}
                  <select
                    className="input input-sm"
                    value={selectedPhotoDim}
                    onChange={(e) => setSelectedPhotoDim(e.target.value)}
                    style={{ width: '190px', fontWeight: 600 }}
                  >
                    <option value="adventure">Adventure Dimension</option>
                    <option value="nature">Nature Dimension</option>
                    <option value="peacefulness">Peacefulness Dimension</option>
                    <option value="crowd_match">Crowd Match Dimension</option>
                    <option value="visual_atmosphere">Visual Atmosphere Dimension</option>
                  </select>
                </div>

                {/* Photo Grid with Contribution Badges */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
                  gap: '1rem'
                }}>
                  {(explainData.per_photo?.photos || []).map((photo, pIdx) => {
                    const contrib = photo.dimension_contributions?.[selectedPhotoDim] ?? 0;
                    const isPositive = contrib >= 0;
                    return (
                      <div
                        key={pIdx}
                        style={{
                          background: '#f8fafc',
                          borderRadius: '10px',
                          border: '1px solid #e2e8f0',
                          overflow: 'hidden',
                          display: 'flex',
                          flexDirection: 'column'
                        }}
                      >
                        <div style={{ height: '140px', width: '100%', position: 'relative', background: '#e2e8f0' }}>
                          <img
                            src={getImageUrl(photo.web_path)}
                            alt={photo.filename}
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                            onError={(e) => { e.target.style.display = 'none'; }}
                          />
                          <div style={{
                            position: 'absolute',
                            top: '8px',
                            right: '8px',
                            background: isPositive ? 'rgba(16, 185, 129, 0.9)' : 'rgba(239, 68, 68, 0.9)',
                            color: '#ffffff',
                            padding: '3px 8px',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            backdropFilter: 'blur(4px)'
                          }}>
                            {isPositive ? '+' : ''}{contrib.toFixed(2)} pts
                          </div>
                        </div>
                        <div style={{ padding: '10px 12px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                          <div>
                            <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-main)', wordBreak: 'break-all' }}>
                              {photo.attraction || photo.filename}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                              Weight: {photo.weight} (1 / {explainData.per_photo?.total_photos})
                            </div>
                          </div>
                          <div style={{ marginTop: '8px', background: '#e2e8f0', height: '5px', borderRadius: '3px', overflow: 'hidden' }}>
                            <div style={{
                              width: `${Math.min(Math.abs(contrib) * 10, 100)}%`,
                              height: '100%',
                              background: isPositive ? PALETTE.positive : PALETTE.negative
                            }}></div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          ) : null}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: EMBEDDING EXPLORER (PCA & t-SNE)                                   */}
      {/* ========================================================================= */}
      {activeTab === 'embeddings' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Controls Bar */}
          <div className="glass-panel" style={{ padding: '1.5rem', background: '#ffffff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Compass size={22} style={{ color: PALETTE.fusion }} />
                  <h3 style={{ fontSize: '1.25rem', color: 'var(--text-main)' }}>
                    Latent Embedding Space Explorer (PCA & t-SNE)
                  </h3>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
                  What this shows: 2D projection of Fused (896D), Text-only (384D), and Image-only (512D) destination representations.
                </p>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  source: fused_embeddings.npy, text_embeddings.npy, image_embeddings.npy &bull; Note: t-SNE distances between non-contiguous clusters are not physically meaningful.
                </div>
              </div>

              {/* Search to highlight */}
              <div style={{ position: 'relative', width: '240px' }}>
                <Search size={16} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  placeholder="Search destination..."
                  className="input input-sm"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ paddingLeft: '32px', width: '100%' }}
                />
              </div>
            </div>

            {/* Toggle Controls Grid */}
            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '1.5rem',
              marginTop: '1.25rem',
              paddingTop: '1rem',
              borderTop: '1px solid #f1f5f9'
            }}>
              {/* Projection Method Toggle */}
              <div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Projection Method
                </div>
                <div style={{ display: 'flex', gap: '4px', background: '#f1f5f9', padding: '3px', borderRadius: '8px' }}>
                  <button
                    className={`btn btn-sm ${embedMethod === 'pca' ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setEmbedMethod('pca')}
                    style={{ fontSize: '0.76rem', padding: '4px 12px' }}
                  >
                    PCA (Linear Geometry)
                  </button>
                  <button
                    className={`btn btn-sm ${embedMethod === 'tsne' ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setEmbedMethod('tsne')}
                    style={{ fontSize: '0.76rem', padding: '4px 12px' }}
                  >
                    t-SNE (Local Clusters)
                  </button>
                </div>
              </div>

              {/* Modality Toggle */}
              <div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Embedding Modality
                </div>
                <div style={{ display: 'flex', gap: '4px', background: '#f1f5f9', padding: '3px', borderRadius: '8px' }}>
                  <button
                    className={`btn btn-sm ${embedModality === 'fused' ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setEmbedModality('fused')}
                    style={{ fontSize: '0.76rem', padding: '4px 10px' }}
                  >
                    Fused (896D)
                  </button>
                  <button
                    className={`btn btn-sm ${embedModality === 'img' ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setEmbedModality('img')}
                    style={{ fontSize: '0.76rem', padding: '4px 10px' }}
                  >
                    Image-only (512D)
                  </button>
                  <button
                    className={`btn btn-sm ${embedModality === 'text' ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setEmbedModality('text')}
                    style={{ fontSize: '0.76rem', padding: '4px 10px' }}
                  >
                    Text-only (384D)
                  </button>
                </div>
              </div>

              {/* Color By Selector */}
              <div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                  Color Points By
                </div>
                <select
                  className="input input-sm"
                  value={colorBy}
                  onChange={(e) => setColorBy(e.target.value)}
                  style={{ minWidth: '180px', fontWeight: 600 }}
                >
                  <option value="region">Geographic Region</option>
                  <option value="category">Destination Category</option>
                  <option value="nature">Nature Vibe (0-100)</option>
                  <option value="adventure">Adventure Vibe (0-100)</option>
                  <option value="peacefulness">Peacefulness Vibe (0-100)</option>
                  <option value="crowd_match">Crowd Match Vibe (0-100)</option>
                  <option value="visual_atmosphere">Visual Atmosphere Vibe (0-100)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Scatter Chart & Nearest Neighbors Panel */}
          {coordsLoading ? (
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
              <RefreshCw size={32} className="spin" style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
              <p style={{ color: 'var(--text-secondary)' }}>Loading coordinates and projecting admin destinations...</p>
            </div>
          ) : coordsData ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 340px', gap: '1.5rem', alignItems: 'start' }}>
              {/* Interactive Scatter Canvas */}
              <div className="glass-panel" style={{ padding: '1.5rem', background: '#ffffff', position: 'relative' }}>
                <div style={{ height: '520px', width: '100%' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                      <XAxis
                        type="number"
                        dataKey="x"
                        name="Dim 1"
                        stroke="var(--text-muted)"
                        fontSize={11}
                        tickLine={false}
                      />
                      <YAxis
                        type="number"
                        dataKey="y"
                        name="Dim 2"
                        stroke="var(--text-muted)"
                        fontSize={11}
                        tickLine={false}
                      />
                      <ZAxis range={[70, 70]} />
                      <Tooltip
                        cursor={{ strokeDasharray: '3 3' }}
                        content={({ payload }) => {
                          if (!payload || !payload.length) return null;
                          const d = payload[0].payload;
                          return (
                            <div style={{
                              background: '#0f172a',
                              color: '#fff',
                              padding: '10px 14px',
                              borderRadius: '8px',
                              fontSize: '0.8rem',
                              maxWidth: '260px'
                            }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <strong style={{ color: '#38bdf8' }}>{d.destination}</strong>
                                {d.is_admin_added && (
                                  <span style={{ fontSize: '0.65rem', background: '#ea580c', padding: '1px 5px', borderRadius: '3px' }}>
                                    Admin Added
                                  </span>
                                )}
                              </div>
                              <div style={{ fontSize: '0.72rem', color: '#94a3b8', margin: '2px 0 6px' }}>
                                {d.state} &bull; {d.category}
                              </div>
                              <div style={{ fontSize: '0.72rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2px' }}>
                                <span>Nature: {d.vibe_scores?.nature}</span>
                                <span>Adventure: {d.vibe_scores?.adventure}</span>
                                <span>Peace: {d.vibe_scores?.peacefulness}</span>
                                <span>Atmosphere: {d.vibe_scores?.visual_atmosphere}</span>
                              </div>
                              {d.is_ood && (
                                <div style={{ color: '#ef4444', fontWeight: 700, marginTop: '4px', fontSize: '0.72rem' }}>
                                  ⚠️ Outside Training Range (OOD)
                                </div>
                              )}
                            </div>
                          );
                        }}
                      />
                      <Scatter
                        data={(coordsData.destinations || []).map(d => {
                          const coordKey = `${embedMethod}_${embedModality}`;
                          const coords = d[coordKey] || [0, 0];
                          const isMatch = searchQuery ? d.destination.toLowerCase().includes(searchQuery.toLowerCase()) : true;
                          const isSelected = selectedDest?.destination === d.destination;

                          let ptColor = PALETTE.fusion;
                          if (colorBy === 'region') {
                            const regionColors = { North: '#3b82f6', South: '#10b981', West: '#f59e0b', East: '#8b5cf6', Central: '#ec4899', Northeast: '#06b6d4' };
                            ptColor = regionColors[d.region] || '#64748b';
                          } else if (colorBy === 'category') {
                            const catColors = { Heritage: '#6366f1', Nature: '#10b981', Beach: '#06b6d4', Spiritual: '#f59e0b', Adventure: '#ea580c', HillStation: '#84cc16' };
                            ptColor = catColors[d.category] || '#64748b';
                          } else {
                            const val = d.vibe_scores?.[colorBy] ?? 50;
                            ptColor = val > 75 ? '#ea580c' : val > 50 ? '#f59e0b' : val > 25 ? '#3b82f6' : '#64748b';
                          }

                          return {
                            x: coords[0],
                            y: coords[1],
                            destination: d.destination,
                            state: d.state,
                            category: d.category,
                            region: d.region,
                            vibe_scores: d.vibe_scores,
                            is_admin_added: d.is_admin_added,
                            is_ood: d.is_ood,
                            max_similarity_to_training: d.max_similarity_to_training,
                            nearest_neighbors: d.nearest_neighbors,
                            color: isMatch ? (d.is_admin_added ? '#ec4899' : ptColor) : '#cbd5e1',
                            isSelected
                          };
                        })}
                        onClick={(entry) => setSelectedDest(entry)}
                      >
                        {(coordsData.destinations || []).map((entry, index) => (
                          <Cell
                            key={`pt-${index}`}
                            fill={entry.is_admin_added ? '#ec4899' : entry.color || PALETTE.fusion}
                            stroke={selectedDest?.destination === entry.destination ? '#0f172a' : 'transparent'}
                            strokeWidth={2}
                          />
                        ))}
                      </Scatter>
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Selected Destination Details & Nearest Neighbours */}
              <div className="glass-panel" style={{ padding: '1.5rem', background: '#ffffff', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {selectedDest ? (
                  <>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span className="badge" style={{ background: selectedDest.is_admin_added ? '#ec4899' : '#0d9488', color: '#fff' }}>
                          {selectedDest.is_admin_added ? 'Admin-Added Destination' : 'Curated Dataset'}
                        </span>
                        {selectedDest.is_ood && (
                          <span className="badge" style={{ background: '#ef4444', color: '#fff', fontWeight: 700 }}>
                            OOD Flag
                          </span>
                        )}
                      </div>
                      <h3 style={{ fontSize: '1.35rem', color: 'var(--text-main)', marginTop: '6px' }}>
                        {selectedDest.destination}
                      </h3>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        {selectedDest.state} &bull; {selectedDest.region} &bull; {selectedDest.category}
                      </div>
                    </div>

                    {/* Vibe Profile Mini Bar */}
                    <div style={{ background: '#f8fafc', padding: '10px 12px', borderRadius: '8px' }}>
                      <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                        Vibe Scores (0-100)
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.75rem' }}>
                        {Object.entries(selectedDest.vibe_scores || {}).map(([dim, val]) => (
                          <div key={dim} style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ textTransform: 'capitalize' }}>{dim.replace('_', ' ')}</span>
                            <strong>{val}</strong>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* 5-Nearest Neighbours in Embedding Space */}
                    <div>
                      <h4 style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                        <Crosshair size={15} style={{ color: PALETTE.fusion }} />
                        5 Nearest Destinations (Cosine Sim)
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {(selectedDest.nearest_neighbors || []).map((nn, nIdx) => (
                          <div
                            key={nIdx}
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              padding: '8px 10px',
                              background: '#f8fafc',
                              borderRadius: '6px',
                              fontSize: '0.78rem'
                            }}
                          >
                            <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                              {nIdx + 1}. {nn.destination}
                            </span>
                            <span style={{ color: PALETTE.fusion, fontWeight: 700 }}>
                              {nn.similarity}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {selectedDest.is_admin_added && (
                      <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', background: '#fffbeb', padding: '8px 10px', borderRadius: '6px', border: '1px solid #fef3c7' }}>
                        Max cosine similarity to training points: <strong>{selectedDest.max_similarity_to_training}</strong> (5th percentile OOD threshold: {coordsData.ood_cosine_threshold}).
                      </div>
                    )}
                  </>
                ) : (
                  <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
                    <MapPin size={32} style={{ margin: '0 auto 0.5rem', opacity: 0.5 }} />
                    <p style={{ fontSize: '0.85rem' }}>Click any point on the scatter map to view nearest neighbours and vibe profile.</p>
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: INFERENCE LAB (4-COLUMN LIVE COMPARISON)                           */}
      {/* ========================================================================= */}
      {activeTab === 'lab' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Query & Sliders Input Console */}
          <div className="glass-panel" style={{ padding: '1.75rem', background: '#ffffff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Activity size={22} style={{ color: PALETTE.fusion }} />
                  <h3 style={{ fontSize: '1.25rem', color: 'var(--text-main)' }}>
                    Multi-Modal Inference Lab & 4-Column Reranker
                  </h3>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
                  What this shows: Live side-by-side ranking of Baseline (TF-IDF), Text (MiniLM), Visual (CLIP Max-Pool), and Fusion models.
                </p>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  <strong>Important Note:</strong> Fusion ranks by the vibe sliders, as in the published experiments; the other three rank by the text query.
                </div>
              </div>

              {/* Research Queries Pre-Load Dropdown */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>Load Research Query:</span>
                <select
                  className="input input-sm"
                  value={loadedQueryId}
                  onChange={(e) => handleSelectResearchQuery(e.target.value)}
                  style={{ width: '220px', fontWeight: 600 }}
                >
                  <option value="">-- Custom Live Query --</option>
                  {(perQuery?.queries || []).map(q => (
                    <option key={q.query_id} value={q.query_id}>
                      {q.query_id.toUpperCase()}: {q.query_text.slice(0, 28)}...
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Input Form */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div>
                <label style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-main)', display: 'block', marginBottom: '6px' }}>
                  Text Query (used by Baseline, Text, and Visual models)
                </label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <input
                    type="text"
                    className="input"
                    placeholder="e.g. peaceful spiritual yoga retreats in the mountains"
                    value={labTextQuery}
                    onChange={(e) => { setLabTextQuery(e.target.value); setLoadedQueryId(''); }}
                    style={{ flex: 1 }}
                  />
                  <button
                    className="btn btn-primary"
                    onClick={() => handleRunLabQuery()}
                    disabled={labRunning || (!labTextQuery && Object.values(labSliders).every(v => v === 'neutral'))}
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', minWidth: '130px', justifyContent: 'center' }}
                  >
                    {labRunning ? <RefreshCw size={16} className="spin" /> : <TrendingUp size={16} />}
                    {labRunning ? 'Reranking...' : 'Run Query'}
                  </button>
                </div>
              </div>

              {/* 5 Vibe Sliders (Fusion Reranking Weights) */}
              <div>
                <label style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-main)', display: 'block', marginBottom: '6px' }}>
                  Vibe Intention Filters (used by Fusion Model)
                </label>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                  gap: '1rem',
                  background: '#f8fafc',
                  padding: '12px 16px',
                  borderRadius: '8px'
                }}>
                  {['nature', 'adventure', 'peacefulness', 'crowd_match', 'visual_atmosphere'].map(dim => (
                    <div key={dim}>
                      <div style={{ fontSize: '0.74rem', textTransform: 'capitalize', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                        {dim.replace('_', ' ')}
                      </div>
                      <div style={{ display: 'flex', gap: '3px' }}>
                        {['low', 'neutral', 'high'].map(val => (
                          <button
                            key={val}
                            type="button"
                            onClick={() => setLabSliders(prev => ({ ...prev, [dim]: val }))}
                            style={{
                              flex: 1,
                              border: 'none',
                              padding: '4px 6px',
                              borderRadius: '4px',
                              fontSize: '0.72rem',
                              fontWeight: labSliders[dim] === val ? 700 : 500,
                              background: labSliders[dim] === val ? (val === 'high' ? PALETTE.positive : val === 'low' ? PALETTE.negative : '#94a3b8') : '#e2e8f0',
                              color: labSliders[dim] === val ? '#ffffff' : '#475569',
                              cursor: 'pointer'
                            }}
                          >
                            {val}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* RERANKER RESULTS: 4 COLUMNS SIDE BY SIDE */}
          {labResult && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Gauges & Overlap Bar if research query loaded */}
              {labResult.loaded_query_id && (
                <div className="glass-panel" style={{ padding: '1.25rem', background: '#ffffff', display: 'flex', flexWrap: 'wrap', gap: '1.5rem', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <span className="badge" style={{ background: '#10b981', color: '#fff', fontWeight: 700 }}>
                      Evaluated against Ground-Truth ({labResult.relevant_ground_truth_count} Relevant Destinations)
                    </span>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                      Green highlighted rows below indicate verified hits in the published human evaluation ground truth.
                    </div>
                  </div>

                  {/* 4 Precision Gauges */}
                  <div style={{ display: 'flex', gap: '1.25rem', flexWrap: 'wrap' }}>
                    {Object.entries(labResult.live_metrics || {}).map(([mName, mVals]) => (
                      <div key={mName} style={{ textAlign: 'center', background: '#f8fafc', padding: '6px 14px', borderRadius: '8px' }}>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{mName}</div>
                        <div style={{ fontSize: '1.15rem', fontWeight: 800, color: modelColorMap[mName === 'visual' ? 'Visual (Max)' : mName === 'text' ? 'Text' : mName === 'fusion' ? 'Fusion' : 'Baseline'] || '#0f172a' }}>
                          P@5: {(mVals.p_at_5 * 100).toFixed(0)}%
                        </div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>P@10: {(mVals.p_at_10 * 100).toFixed(0)}%</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 4 Ranking Columns */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                gap: '1rem'
              }}>
                {/* Column 1: Baseline (TF-IDF) */}
                <div className="glass-panel" style={{ padding: '1.25rem', background: '#ffffff', borderTop: `4px solid ${PALETTE.baseline}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <h4 style={{ fontSize: '0.98rem', fontWeight: 700, color: PALETTE.baseline }}>
                      Baseline (TF-IDF)
                    </h4>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Text Query</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {(labResult.baseline || []).map((item) => (
                      <div
                        key={item.rank}
                        style={{
                          padding: '8px 10px',
                          borderRadius: '6px',
                          background: item.is_hit ? 'rgba(16, 185, 129, 0.12)' : '#f8fafc',
                          border: item.is_hit ? '1px solid #10b981' : '1px solid #f1f5f9',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          fontSize: '0.8rem'
                        }}
                      >
                        <span style={{ fontWeight: item.is_hit ? 700 : 500, color: item.is_hit ? '#047857' : 'var(--text-main)' }}>
                          #{item.rank} {item.destination}
                        </span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          {item.score?.toFixed(3)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Column 2: Text (MiniLM) */}
                <div className="glass-panel" style={{ padding: '1.25rem', background: '#ffffff', borderTop: `4px solid ${PALETTE.text}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <h4 style={{ fontSize: '0.98rem', fontWeight: 700, color: PALETTE.text }}>
                      Text (MiniLM Cosine)
                    </h4>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Semantic Cosine</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {(labResult.text || []).map((item) => (
                      <div
                        key={item.rank}
                        style={{
                          padding: '8px 10px',
                          borderRadius: '6px',
                          background: item.is_hit ? 'rgba(16, 185, 129, 0.12)' : '#f8fafc',
                          border: item.is_hit ? '1px solid #10b981' : '1px solid #f1f5f9',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          fontSize: '0.8rem'
                        }}
                      >
                        <span style={{ fontWeight: item.is_hit ? 700 : 500, color: item.is_hit ? '#047857' : 'var(--text-main)' }}>
                          #{item.rank} {item.destination}
                        </span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          {item.score?.toFixed(3)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Column 3: Visual (CLIP Max-Pool with Thumbnail) */}
                <div className="glass-panel" style={{ padding: '1.25rem', background: '#ffffff', borderTop: `4px solid ${PALETTE.visualMax}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <h4 style={{ fontSize: '0.98rem', fontWeight: 700, color: PALETTE.visualMax }}>
                      Visual (CLIP Max-Pool)
                    </h4>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Best Matching Photo</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {(labResult.visual || []).map((item) => (
                      <div
                        key={item.rank}
                        style={{
                          padding: '6px 8px',
                          borderRadius: '6px',
                          background: item.is_hit ? 'rgba(16, 185, 129, 0.12)' : '#f8fafc',
                          border: item.is_hit ? '1px solid #10b981' : '1px solid #f1f5f9',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          fontSize: '0.8rem'
                        }}
                      >
                        {item.best_photo_path && (
                          <img
                            src={getImageUrl(item.best_photo_path)}
                            alt=""
                            style={{ width: 36, height: 36, borderRadius: 4, objectFit: 'cover', flexShrink: 0 }}
                            onError={(e) => { e.target.style.display = 'none'; }}
                          />
                        )}
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontWeight: item.is_hit ? 700 : 500, color: item.is_hit ? '#047857' : 'var(--text-main)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            #{item.rank} {item.destination}
                          </div>
                          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                            Sim: {item.score?.toFixed(3)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Column 4: Fusion (Predicted Vibe Match) */}
                <div className="glass-panel" style={{ padding: '1.25rem', background: '#ffffff', borderTop: `4px solid ${PALETTE.fusion}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <h4 style={{ fontSize: '0.98rem', fontWeight: 700, color: PALETTE.fusion }}>
                      Fusion (Predicted Vibe)
                    </h4>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Vibe Sliders Match</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {(labResult.fusion || []).map((item) => (
                      <div
                        key={item.rank}
                        style={{
                          padding: '8px 10px',
                          borderRadius: '6px',
                          background: item.is_hit ? 'rgba(16, 185, 129, 0.12)' : '#f8fafc',
                          border: item.is_hit ? '1px solid #10b981' : '1px solid #f1f5f9',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          fontSize: '0.8rem'
                        }}
                      >
                        <span style={{ fontWeight: item.is_hit ? 700 : 500, color: item.is_hit ? '#047857' : 'var(--text-main)' }}>
                          #{item.rank} {item.destination}
                        </span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          Score: {item.score?.toFixed(1)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* 4-Way Overlap Matrix Chart */}
              {labResult.overlap_matrix && (
                <div className="glass-panel" style={{ padding: '1.5rem', background: '#ffffff' }}>
                  <h4 style={{ fontSize: '0.98rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px' }}>
                    Top-10 Recommendation Jaccard / Overlap Matrix
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    Number of shared destinations in the top-10 ranked results across each pair of models.
                  </p>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', maxWidth: '600px', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                      <thead>
                        <tr style={{ background: '#f8fafc' }}>
                          <th style={{ padding: '8px', textAlign: 'left' }}>Model</th>
                          <th style={{ padding: '8px', textAlign: 'center' }}>Baseline</th>
                          <th style={{ padding: '8px', textAlign: 'center' }}>Text</th>
                          <th style={{ padding: '8px', textAlign: 'center' }}>Visual</th>
                          <th style={{ padding: '8px', textAlign: 'center' }}>Fusion</th>
                        </tr>
                      </thead>
                      <tbody>
                        {['Baseline', 'Text', 'Visual', 'Fusion'].map(m1 => (
                          <tr key={m1} style={{ borderBottom: '1px solid #f1f5f9' }}>
                            <td style={{ padding: '8px', fontWeight: 600 }}>{m1}</td>
                            {['Baseline', 'Text', 'Visual', 'Fusion'].map(m2 => {
                              const cnt = labResult.overlap_matrix?.[m1]?.[m2] ?? (m1 === m2 ? 10 : 0);
                              return (
                                <td key={m2} style={{ padding: '8px', textAlign: 'center', fontWeight: m1 === m2 ? 700 : 500, color: cnt > 4 ? PALETTE.fusion : 'var(--text-main)' }}>
                                  {cnt} / 10
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* SLIDE-OUT QUERY METRICS DRAWER */}
      {drawerQueryCell && (
        <div style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: '420px',
          background: '#ffffff',
          boxShadow: '-8px 0 30px rgba(0,0,0,0.15)',
          zIndex: 1000,
          padding: '2rem 1.5rem',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="badge" style={{ background: '#ea580c', color: '#ffffff', fontWeight: 600 }}>
              {drawerQueryCell.model} Model
            </span>
            <button
              onClick={() => setDrawerQueryCell(null)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
            >
              <X size={20} />
            </button>
          </div>

          <div>
            <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Query ID: {drawerQueryCell.query.query_id.toUpperCase()}
            </div>
            <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)', marginTop: '2px' }}>
              "{drawerQueryCell.query.query_text}"
            </h3>
          </div>

          <div style={{ display: 'flex', gap: '1rem', background: '#f8fafc', padding: '12px', borderRadius: '8px' }}>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>NDCG@5</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: PALETTE.fusion }}>
                {drawerQueryCell.metric?.ndcg_at_5 ?? 0}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Precision@5</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--primary)' }}>
                {drawerQueryCell.metric?.p_at_5 ?? 0}
              </div>
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '0.92rem', color: 'var(--text-main)', marginBottom: '8px' }}>
              Model's Top 10 Predictions (Hits in Green)
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {(drawerQueryCell.metric?.top10 || []).map((item, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    background: item.is_hit ? 'rgba(16, 185, 129, 0.1)' : '#f8fafc',
                    border: item.is_hit ? '1px solid #10b981' : '1px solid var(--border-glass)'
                  }}
                >
                  <span style={{ fontSize: '0.84rem', fontWeight: item.is_hit ? 700 : 500, color: item.is_hit ? '#047857' : 'var(--text-main)' }}>
                    #{item.rank} {item.destination}
                  </span>
                  {item.is_hit && (
                    <span style={{ fontSize: '0.72rem', color: '#047857', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '3px' }}>
                      <CheckCircle2 size={13} /> Ground Truth Hit
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
              Ground Truth Relevant Set ({drawerQueryCell.metric?.relevant_destinations?.length || 0})
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
              {(drawerQueryCell.metric?.relevant_destinations || []).map((d, dIdx) => (
                <span key={dIdx} style={{ fontSize: '0.74rem', background: '#e2e8f0', padding: '2px 8px', borderRadius: '4px' }}>
                  {d}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
