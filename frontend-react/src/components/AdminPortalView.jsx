import React, { useState, useEffect } from 'react';
import {
  Shield, Check, X, Users, AlertTriangle, PlusCircle, Sparkles,
  MapPin, CheckCircle, RefreshCw, EyeOff, Eye, Compass, CreditCard,
  BarChart2, TrendingUp, Layers, Cpu, Award, UserCheck, CheckCircle2
} from 'lucide-react';
import {
  getAdminSubmissions, approveAdminSubmission, rejectAdminSubmission,
  getAdminUsers, toggleAdminUserActive, toggleAdminUserVerify, getAdminReports, resolveAdminReport,
  createAdminDestination, getAdminDlBenchmarks
} from '../api';
import DeepLearningDashboardView from './DeepLearningDashboardView';

export default function AdminPortalView() {
  const [activeTab, setActiveTab] = useState('submissions');

  // Submissions state
  const [submissions, setSubmissions] = useState([]);
  const [subLoading, setSubLoading] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [rejectingId, setRejectingId] = useState(null);

  // Users state
  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [userRoleFilter, setUserRoleFilter] = useState('all');

  // Reports state
  const [reports, setReports] = useState([]);
  const [reportsLoading, setReportsLoading] = useState(false);

  // New Destination Creator state
  const [destName, setDestName] = useState('');
  const [destState, setDestState] = useState('');
  const [destRegion, setDestRegion] = useState('North');
  const [destCategory, setDestCategory] = useState('Hills');
  const [destDesc, setDestDesc] = useState('');
  const [destAttractions, setDestAttractions] = useState('');
  const [destBestTime, setDestBestTime] = useState('October to March');
  const [selectedPhotos, setSelectedPhotos] = useState([]);
  const [creatingDest, setCreatingDest] = useState(false);
  const [createdDestResult, setCreatedDestResult] = useState(null);
  const [destError, setDestError] = useState('');

  // DL Benchmarks state
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [benchmarksLoading, setBenchmarksLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'submissions') loadSubmissions();
    if (activeTab === 'users') loadUsers();
    if (activeTab === 'reports') loadReports();
    if (activeTab === 'dl-benchmarks') loadBenchmarks();
  }, [activeTab]);

  const loadBenchmarks = async () => {
    try {
      setBenchmarksLoading(true);
      const res = await getAdminDlBenchmarks();
      setBenchmarkData(res);
    } catch (err) {
      console.error('Failed to load DL benchmarks', err);
    } finally {
      setBenchmarksLoading(false);
    }
  };

  const loadSubmissions = async () => {
    try {
      setSubLoading(true);
      const res = await getAdminSubmissions('pending');
      setSubmissions(res.submissions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setSubLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      await approveAdminSubmission(id);
      alert('Submission approved and published!');
      loadSubmissions();
    } catch (err) {
      alert(err.message || 'Approval failed');
    }
  };

  const handleReject = async (id) => {
    try {
      await rejectAdminSubmission(id, rejectReason || 'Does not meet guidelines');
      setRejectingId(null);
      setRejectReason('');
      loadSubmissions();
    } catch (err) {
      alert(err.message || 'Rejection failed');
    }
  };

  const loadUsers = async () => {
    try {
      setUsersLoading(true);
      const res = await getAdminUsers();
      setUsers(res.users || []);
    } catch (err) {
      console.error(err);
    } finally {
      setUsersLoading(false);
    }
  };

  const handleToggleUser = async (userId) => {
    try {
      const res = await toggleAdminUserActive(userId);
      alert(res.message);
      loadUsers();
    } catch (err) {
      alert(err.message || 'Failed to update user status');
    }
  };

  const handleToggleVerify = async (userId) => {
    try {
      const res = await toggleAdminUserVerify(userId);
      alert(res.message);
      loadUsers();
    } catch (err) {
      alert(err.message || 'Failed to update verification status');
    }
  };

  const loadReports = async () => {
    try {
      setReportsLoading(true);
      const res = await getAdminReports();
      setReports(res.reports || []);
    } catch (err) {
      console.error(err);
    } finally {
      setReportsLoading(false);
    }
  };

  const handleResolveReport = async (id) => {
    const action = prompt('Enter action taken (e.g. "User warned", "No violation"):');
    if (!action) return;
    try {
      await resolveAdminReport(id, action);
      alert('Report marked as resolved');
      loadReports();
    } catch (err) {
      alert(err.message || 'Failed to resolve report');
    }
  };

  const handleCreateDestination = async (e) => {
    e.preventDefault();
    setDestError('');
    setCreatedDestResult(null);

    if (selectedPhotos.length === 0) {
      setDestError('Please attach at least one photo for CLIP visual embedding extraction.');
      return;
    }

    try {
      setCreatingDest(true);
      const fd = new FormData();
      fd.append('name', destName);
      fd.append('state', destState);
      fd.append('region', destRegion);
      fd.append('category', destCategory);
      fd.append('description', destDesc);
      fd.append('top_attractions', destAttractions);
      fd.append('best_time', destBestTime);

      for (let i = 0; i < selectedPhotos.length; i++) {
        fd.append('photos', selectedPhotos[i]);
      }

      const res = await createAdminDestination(fd);
      setCreatedDestResult(res);
      // Reset form
      setDestName('');
      setDestDesc('');
      setSelectedPhotos([]);
    } catch (err) {
      setDestError(err.message || 'Failed to create destination');
    } finally {
      setCreatingDest(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
        <div style={{ background: 'rgba(245,158,11,0.2)', padding: '0.6rem', borderRadius: 'var(--radius-md)', color: '#fbbf24' }}>
          <Shield size={24} />
        </div>
        <div>
          <h2 style={{ fontSize: '1.75rem' }}>Administrator Console</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            System moderation, submissions queue, user governance & multi-modal AI destination pipeline
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="tab-list">
        <button
          className={`tab-item ${activeTab === 'submissions' ? 'active' : ''}`}
          onClick={() => setActiveTab('submissions')}
        >
          Submission Queue ({submissions.length})
        </button>
        <button
          className={`tab-item ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          User Accounts
        </button>
        <button
          className={`tab-item ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          Safety Reports
        </button>
        <button
          className={`tab-item ${activeTab === 'create-dest' ? 'active' : ''}`}
          onClick={() => setActiveTab('create-dest')}
        >
          + AI Destination Creator
        </button>
        <button
          className={`tab-item ${activeTab === 'dl-benchmarks' ? 'active' : ''}`}
          onClick={() => setActiveTab('dl-benchmarks')}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}
        >
          <BarChart2 size={15} style={{ color: '#4f46e5' }} /> 🧠 DL Benchmark & Model Center
        </button>
      </div>

      {/* 1. SUBMISSION QUEUE */}
      {activeTab === 'submissions' && (
        <div>
          {subLoading ? (
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
              <p style={{ color: 'var(--text-secondary)' }}>Loading submissions queue...</p>
            </div>
          ) : submissions.length === 0 ? (
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
              <CheckCircle size={36} style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
              <h3>All clear! No pending submissions</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.4rem' }}>
                All local contributor spots have been reviewed.
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {submissions.map((sub) => (
                <div key={sub.id} className="glass-panel" style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <h3 style={{ fontSize: '1.25rem' }}>{sub.name}</h3>
                        <span className="badge" style={{ background: 'var(--bg-elevated)', color: 'var(--text-main)', border: '1px solid var(--border-glass)' }}>
                          {sub.category}
                        </span>
                        <span className="badge badge-admin">
                          Destination: {sub.destination}
                        </span>
                      </div>

                      <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem', marginTop: '4px' }}>
                        Submitted by: {sub.submitted_by_name || 'Local Contributor'} ({sub.submitted_at || 'Recently'})
                      </div>

                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: '0.8rem 0', lineHeight: 1.5 }}>
                        {sub.description}
                      </p>

                      {sub.address && (
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          <strong>Address: </strong> {sub.address}
                        </div>
                      )}
                    </div>

                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <button className="btn btn-primary btn-sm" onClick={() => handleApprove(sub.id)}>
                        <Check size={14} /> Approve & Publish
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => setRejectingId(rejectingId === sub.id ? null : sub.id)}
                      >
                        <X size={14} /> Reject
                      </button>
                    </div>
                  </div>

                  {rejectingId === sub.id && (
                    <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-glass)', display: 'flex', gap: '0.5rem' }}>
                      <input
                        type="text"
                        className="input-field"
                        placeholder="Reason for rejection (e.g. duplicate place, insufficient detail)..."
                        value={rejectReason}
                        onChange={(e) => setRejectReason(e.target.value)}
                      />
                      <button className="btn btn-danger btn-sm" onClick={() => handleReject(sub.id)}>
                        Confirm Reject
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 2. USER ACCOUNTS REGISTRY */}
      {activeTab === 'users' && (
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Users size={20} color="var(--primary)" />
                Registered Community Registry ({users.length})
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.82rem', marginTop: '3px' }}>
                Manage verified tourists, local community hosts, and direct payout-licensed guides
              </p>
            </div>

            {/* Role Filter Tabs */}
            <div style={{ display: 'flex', gap: '0.4rem', background: 'rgba(0,0,0,0.25)', padding: '0.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)' }}>
              {[
                { id: 'all', label: 'All Users', count: users.length },
                { id: 'tourist', label: 'Tourists', count: users.filter(u => u.role === 'tourist').length },
                { id: 'local', label: 'Locals', count: users.filter(u => u.role === 'local').length },
                { id: 'guide', label: 'Pro Guides', count: users.filter(u => u.role === 'guide').length }
              ].map(f => (
                <button
                  key={f.id}
                  type="button"
                  onClick={() => setUserRoleFilter(f.id)}
                  style={{
                    padding: '0.4rem 0.85rem',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    borderRadius: 'var(--radius-sm)',
                    border: 'none',
                    cursor: 'pointer',
                    background: userRoleFilter === f.id ? 'var(--primary)' : 'transparent',
                    color: userRoleFilter === f.id ? '#0f172a' : 'var(--text-secondary)',
                    transition: 'all 0.2s ease'
                  }}
                >
                  {f.label} ({f.count})
                </button>
              ))}
            </div>
          </div>

          {/* Quick Info Box for Guides */}
          {userRoleFilter === 'guide' && (
            <div style={{
              background: 'linear-gradient(135deg, rgba(16,185,129,0.12), rgba(6,182,212,0.1))',
              border: '1px solid rgba(16,185,129,0.3)',
              borderRadius: 'var(--radius-md)',
              padding: '0.85rem 1.15rem',
              marginBottom: '1.25rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '0.75rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <CreditCard size={22} color="#10b981" />
                <div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#34d399' }}>
                    Direct Guide Connection & Payout Gateway Enabled
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                    All 20 certified guides have direct UPI / bank payout access for instant traveler booking settlements without middleman fees.
                  </div>
                </div>
              </div>
              <span className="badge" style={{ background: '#10b981', color: '#064e3b', fontWeight: 700 }}>
                20 Certified Guides Active
              </span>
            </div>
          )}

          {usersLoading ? (
            <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem' }}>Loading user registry...</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-glass)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem' }}>Name & Location</th>
                    <th style={{ padding: '0.75rem' }}>Contact & Credentials</th>
                    <th style={{ padding: '0.75rem' }}>Role</th>
                    <th style={{ padding: '0.75rem' }}>Direct Payout / Details</th>
                    <th style={{ padding: '0.75rem' }}>Status</th>
                    <th style={{ padding: '0.75rem', textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {users
                    .filter(u => userRoleFilter === 'all' || u.role === userRoleFilter)
                    .map((u) => (
                      <tr key={u.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                        <td style={{ padding: '0.75rem' }}>
                          <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.9rem' }}>
                            {u.name}
                            {u.is_demo && (
                              <span className="badge" style={{ marginLeft: '0.4rem', background: 'var(--bg-elevated)', color: 'var(--text-muted)', border: '1px solid var(--border-glass)', fontSize: '0.68rem' }}>
                                Demo
                              </span>
                            )}
                          </div>
                          <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '0.25rem', marginTop: '2px' }}>
                            <MapPin size={12} /> {u.home_city || 'India'}
                          </div>
                        </td>
                        <td style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>
                          <div>{u.email}</div>
                          {u.interest_tags && (
                            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                              Tags: {u.interest_tags.split(',').slice(0, 3).join(', ')}
                            </div>
                          )}
                        </td>
                        <td style={{ padding: '0.75rem' }}>
                          <span
                            className="badge"
                            style={{
                              background:
                                u.role === 'admin' ? 'rgba(239,68,68,0.2)' :
                                u.role === 'guide' ? 'rgba(16,185,129,0.2)' :
                                u.role === 'local' ? 'rgba(245,158,11,0.2)' :
                                'rgba(56,189,248,0.15)',
                              color:
                                u.role === 'admin' ? '#f87171' :
                                u.role === 'guide' ? '#34d399' :
                                u.role === 'local' ? '#fbbf24' :
                                '#38bdf8',
                              fontWeight: 600,
                              textTransform: 'uppercase',
                              letterSpacing: '0.04em',
                              fontSize: '0.72rem'
                            }}
                          >
                            {u.role === 'guide' ? 'PRO GUIDE' : u.role}
                          </span>
                        </td>
                        <td style={{ padding: '0.75rem' }}>
                          {u.role === 'guide' ? (
                            <div style={{ fontSize: '0.78rem', color: '#34d399', background: 'rgba(16,185,129,0.08)', padding: '0.35rem 0.55rem', borderRadius: '4px', border: '1px solid rgba(16,185,129,0.2)' }}>
                              <div style={{ fontWeight: 600 }}>{u.contact_info || 'Direct UPI Payout Configured'}</div>
                            </div>
                          ) : (
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                              {u.bio ? u.bio.slice(0, 50) + '...' : 'Verified traveler account'}
                            </div>
                          )}
                        </td>
                        <td style={{ padding: '0.75rem' }}>
                          <span style={{ color: u.is_active ? 'var(--primary)' : '#f87171', fontWeight: 600, fontSize: '0.8rem' }}>
                            {u.is_active ? 'Active' : 'Deactivated'}
                          </span>
                        </td>
                        <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                          <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end', alignItems: 'center' }}>
                            {u.role === 'guide' && (
                              <button
                                className={`btn btn-sm ${u.is_verified ? 'btn-secondary' : 'btn-primary'}`}
                                onClick={() => handleToggleVerify(u.id)}
                                style={{
                                  padding: '0.3rem 0.6rem',
                                  fontSize: '0.75rem',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                  background: u.is_verified ? 'rgba(16,185,129,0.15)' : undefined,
                                  borderColor: u.is_verified ? '#10b981' : undefined,
                                  color: u.is_verified ? '#059669' : undefined
                                }}
                                title={u.is_verified ? "Click to Revoke Verification" : "Click to Approve & Verify Guide"}
                              >
                                <UserCheck size={12} />
                                {u.is_verified ? 'Verified ✓' : 'Verify'}
                              </button>
                            )}

                            {u.role !== 'admin' && (
                              <button
                                className={`btn btn-sm ${u.is_active ? 'btn-danger' : 'btn-primary'}`}
                                onClick={() => handleToggleUser(u.id)}
                                style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                              >
                                {u.is_active ? <EyeOff size={12} /> : <Eye size={12} />}
                                {u.is_active ? 'Deactivate' : 'Reactivate'}
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* 3. SAFETY REPORTS */}
      {activeTab === 'reports' && (
        <div>
          {reportsLoading ? (
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
              <p style={{ color: 'var(--text-secondary)' }}>Loading safety reports...</p>
            </div>
          ) : reports.length === 0 ? (
            <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
              <CheckCircle size={36} style={{ color: 'var(--primary)', margin: '0 auto 1rem' }} />
              <h3>No outstanding reports</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.4rem' }}>
                The traveler community is safe and clean.
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {reports.map((rep) => (
                <div key={rep.id} className="glass-panel" style={{ padding: '1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <span className="badge" style={{ background: 'rgba(239,68,68,0.2)', color: '#f87171' }}>
                          {rep.category.toUpperCase()}
                        </span>
                        <h4 style={{ fontSize: '1rem' }}>Reported User: {rep.reported_user_name}</h4>
                      </div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '4px' }}>
                        Filed by: {rep.reporter_name} on {rep.created_at}
                      </div>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', margin: '0.6rem 0' }}>
                        "{rep.reason}"
                      </p>
                    </div>

                    <div>
                      {rep.status === 'resolved' ? (
                        <span className="badge badge-match">Resolved: {rep.action_taken}</span>
                      ) : (
                        <button className="btn btn-secondary btn-sm" onClick={() => handleResolveReport(rep.id)}>
                          Resolve Report
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 4. AI DESTINATION CREATOR */}
      {activeTab === 'create-dest' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '2rem' }}>
          <div className="glass-panel" style={{ padding: '1.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
              <Sparkles size={20} style={{ color: 'var(--accent-purple)' }} />
              <h3 style={{ fontSize: '1.25rem' }}>Add Destination with Real-Time AI Vibes</h3>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
              Upload local photos to automatically trigger visual feature extraction (fine-tuned CLIP) and Ridge vibe regression inference.
            </p>

            {destError && (
              <div style={{ background: 'rgba(239,68,68,0.15)', color: '#f87171', padding: '0.75rem', borderRadius: 'var(--radius-sm)', marginBottom: '1rem', fontSize: '0.85rem' }}>
                {destError}
              </div>
            )}

            <form onSubmit={handleCreateDestination} style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                    Destination Name *
                  </label>
                  <input
                    type="text"
                    required
                    className="input-field"
                    placeholder="e.g. Ziro Valley"
                    value={destName}
                    onChange={(e) => setDestName(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                    State *
                  </label>
                  <input
                    type="text"
                    required
                    className="input-field"
                    placeholder="e.g. Arunachal Pradesh"
                    value={destState}
                    onChange={(e) => setDestState(e.target.value)}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                    Region
                  </label>
                  <select
                    className="input-field"
                    value={destRegion}
                    onChange={(e) => setDestRegion(e.target.value)}
                    style={{ background: 'var(--bg-card)' }}
                  >
                    <option value="North">North</option>
                    <option value="South">South</option>
                    <option value="East">East</option>
                    <option value="West">West</option>
                    <option value="North East">North East</option>
                    <option value="Central">Central</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                    Category
                  </label>
                  <select
                    className="input-field"
                    value={destCategory}
                    onChange={(e) => setDestCategory(e.target.value)}
                    style={{ background: 'var(--bg-card)' }}
                  >
                    <option value="Hills">Hills & Mountains</option>
                    <option value="Beach">Coastal & Beach</option>
                    <option value="Heritage">Heritage & Culture</option>
                    <option value="Wildlife">Wildlife & Nature</option>
                    <option value="Spiritual">Spiritual & Temple</option>
                  </select>
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                  Description *
                </label>
                <textarea
                  required
                  rows={3}
                  className="input-field"
                  placeholder="Overview of the destination landscape, cultural atmosphere, and vibe..."
                  value={destDesc}
                  onChange={(e) => setDestDesc(e.target.value)}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                  Top Attractions (comma separated)
                </label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Paddy Fields, Tarin Fish Farm, Kardo Shivling"
                  value={destAttractions}
                  onChange={(e) => setDestAttractions(e.target.value)}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                  Upload Photos (1 to 4 images for multi-modal embedding) *
                </label>
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  required
                  onChange={(e) => setSelectedPhotos(e.target.files)}
                  style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                style={{ marginTop: '0.5rem', padding: '0.85rem' }}
                disabled={creatingDest}
              >
                {creatingDest ? 'Running Multi-Modal Inference...' : 'Create & Infer Vibes'}
              </button>
            </form>
          </div>

          {/* AI Result Card */}
          <div>
            {createdDestResult ? (
              <div className="glass-panel" style={{ padding: '1.75rem', border: '1px solid var(--primary)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--primary)', marginBottom: '0.75rem' }}>
                  <CheckCircle size={22} />
                  <h3 style={{ fontSize: '1.25rem' }}>Destination Created Successfully!</h3>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1.5rem' }}>
                  Multi-modal inference computed 5 vibe dimension scores and published the destination into search.
                </p>

                <h4 style={{ fontSize: '1rem', marginBottom: '0.75rem' }}>Inferred Vibe Scores:</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                  {Object.entries(createdDestResult.vibe_scores || {}).map(([dim, val]) => (
                    <div key={dim}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '3px' }}>
                        <span style={{ textTransform: 'capitalize', color: 'var(--text-secondary)' }}>{dim.replace('_', ' ')}</span>
                        <span style={{ fontWeight: 700, color: 'var(--text-main)' }}>{Math.round(val)}/100</span>
                      </div>
                      <div className="vibe-bar-track">
                        <div className="vibe-bar-fill" style={{ width: `${val}%`, background: 'var(--primary)' }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="glass-panel" style={{ padding: '2.5rem', textAlign: 'center' }}>
                <Sparkles size={36} style={{ color: 'var(--accent-purple)', margin: '0 auto 1rem' }} />
                <h3>Real-Time Vibe Estimation</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.5rem', lineHeight: 1.5 }}>
                  When you submit a new destination, the backend extracts image features using fine-tuned CLIP embeddings, averages the visual vectors, and runs 5 trained Ridge regressors to predict scores for Nature, Adventure, Peacefulness, Crowd Match, and Visual Atmosphere.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 5. DL MODEL INTELLIGENCE & BENCHMARK CENTER (/admin/ml) */}
      {activeTab === 'dl-benchmarks' && (
        <DeepLearningDashboardView />
      )}
    </div>
  );
}
