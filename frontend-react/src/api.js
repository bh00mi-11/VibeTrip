const API_BASE = import.meta.env.VITE_API_BASE || (typeof window !== 'undefined' && window.location.port !== '5173' ? window.location.origin : 'http://localhost:8005');

export function getToken() {
  return localStorage.getItem('vibetrip_token');
}

export function setToken(token) {
  if (token) {
    localStorage.setItem('vibetrip_token', token);
  } else {
    localStorage.removeItem('vibetrip_token');
  }
}

export function getUser() {
  const raw = localStorage.getItem('vibetrip_user');
  try {
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

export function setUser(user) {
  if (user) {
    localStorage.setItem('vibetrip_user', JSON.stringify(user));
  } else {
    localStorage.removeItem('vibetrip_user');
  }
}

export function logout() {
  localStorage.removeItem('vibetrip_token');
  localStorage.removeItem('vibetrip_user');
}

function getHeaders(contentType = 'application/json') {
  const headers = {};
  if (contentType) {
    headers['Content-Type'] = contentType;
  }
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = { ...getHeaders(options.contentType !== undefined ? options.contentType : 'application/json'), ...options.headers };
  if (options.contentType === false) {
    delete headers['Content-Type'];
  }

  const res = await fetch(url, {
    ...options,
    headers,
  });

  let data = null;
  const isJson = (res.headers.get('content-type') || '').includes('application/json');
  if (isJson) {
    data = await res.json();
  } else {
    data = await res.text();
  }

  if (!res.ok) {
    const errorMsg = (data && data.detail) || `Request failed with status ${res.status}`;
    const err = new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

// --- AUTH API ---
export async function authLogin(email, password) {
  const res = await request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  if (res.access_token) {
    setToken(res.access_token);
    setUser(res.user);
  }
  return res;
}

export async function authSignup(data) {
  const res = await request('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  if (res.access_token) {
    setToken(res.access_token);
    setUser(res.user);
  }
  return res;
}

export async function getMe() {
  return request('/api/auth/me');
}

export async function updateProfile(data) {
  return request('/api/auth/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// --- CORE DESTINATIONS & RECOMMENDATION ---
export async function recommendDestinations(targetDims, queryText = '') {
  return request('/api/recommend', {
    method: 'POST',
    body: JSON.stringify({
      target_dims: targetDims,
      query_text: queryText,
    }),
  });
}

export async function getDestination(name) {
  return request(`/api/destination/${encodeURIComponent(name)}`);
}

// --- ITINERARIES & SAVED TRIPS ---
export async function generateTripPlan(destination, days = 3, vibePreferences = null) {
  return request('/api/trip-plan', {
    method: 'POST',
    body: JSON.stringify({
      destination,
      days,
      vibe_preferences: vibePreferences,
    }),
  });
}

export async function saveTrip(destination, itinerary) {
  return request('/api/trips/save', {
    method: 'POST',
    body: JSON.stringify({
      destination,
      itinerary,
    }),
  });
}

export async function getMyTrips() {
  return request('/api/trips/my');
}

export async function getSharedTrip(token) {
  return request(`/api/trips/shared/${token}`);
}

// --- LOCAL EXPERIENCES & OSM PLACES ---
export async function getLocalExperiences(destination, category = null, sortVibe = null) {
  const params = new URLSearchParams();
  if (category && category !== 'all') params.append('category', category);
  if (sortVibe) params.append('sort_vibe', sortVibe);
  const q = params.toString() ? `?${params.toString()}` : '';
  return request(`/api/local-experiences/${encodeURIComponent(destination)}${q}`);
}

// --- TRAVELER MATCHING & BUDDIES ---
export async function postBuddyInterest(data) {
  return request('/api/interests/post', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getBuddies(destination) {
  return request(`/api/buddies/${encodeURIComponent(destination)}`);
}

export async function sendBuddyRequest(toUserId, destination, note = '') {
  return request('/api/connections/send', {
    method: 'POST',
    body: JSON.stringify({
      to_user_id: toUserId,
      destination,
      message: note,
    }),
  });
}

export async function getReceivedBuddyRequests() {
  const data = await request('/api/connections/inbox');
  return {
    received_requests: (data.incoming || []).map((r) => ({
      id: r.id,
      from_user_id: r.other_user_id,
      from_user_name: r.other_user_name,
      destination: r.destination,
      note: r.message,
      status: r.status,
      revealed_contact: r.contact_revealed,
      created_at: r.created_at,
    })),
  };
}

export async function getSentBuddyRequests() {
  const data = await request('/api/connections/inbox');
  return {
    sent_requests: (data.outgoing || []).map((r) => ({
      id: r.id,
      to_user_id: r.other_user_id,
      to_user_name: r.other_user_name,
      destination: r.destination,
      note: r.message,
      status: r.status,
      revealed_contact: r.contact_revealed,
      created_at: r.created_at,
    })),
  };
}

export async function acceptBuddyRequest(id) {
  return request(`/api/connections/${id}/respond?action=accept`, { method: 'POST' });
}

export async function declineBuddyRequest(id) {
  return request(`/api/connections/${id}/respond?action=decline`, { method: 'POST' });
}

export async function blockUser(blockedUserId, reason = '') {
  return request('/api/users/block', {
    method: 'POST',
    body: JSON.stringify({
      blocked_user_id: blockedUserId,
      reason,
    }),
  });
}

export async function submitReport(reportedUserId, category, reason, context = '') {
  return request('/api/reports/submit', {
    method: 'POST',
    body: JSON.stringify({
      reported_user_id: reportedUserId,
      category,
      reason,
      context,
    }),
  });
}

// --- LOCAL CONTRIBUTOR ---
export async function submitContributePlace(data) {
  return request('/api/contribute/submit', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getMySubmissions() {
  return request('/api/contribute/my');
}

// --- ADMIN PORTAL ---
export async function getAdminSubmissions(status = 'pending') {
  return request(`/api/admin/submissions?status=${status}`);
}

export async function approveAdminSubmission(id) {
  return request(`/api/admin/submissions/${id}/approve`, { method: 'POST' });
}

export async function rejectAdminSubmission(id, reason = '') {
  return request(`/api/admin/submissions/${id}/reject`, {
    method: 'POST',
    body: JSON.stringify({ reason }),
  });
}

export async function getAdminUsers() {
  return request('/api/admin/users');
}

export async function toggleAdminUserActive(userId) {
  return request(`/api/admin/users/${userId}/toggle-active`, { method: 'POST' });
}

export async function getAdminReports() {
  return request('/api/admin/reports');
}

export async function resolveAdminReport(id, actionTaken) {
  return request(`/api/admin/reports/${id}/resolve`, {
    method: 'POST',
    body: JSON.stringify({ action_taken: actionTaken }),
  });
}

export async function createAdminDestination(formData) {
  return request('/api/admin/destinations/create', {
    method: 'POST',
    contentType: false, // let browser set multipart/form-data boundary
    body: formData,
  });
}

export async function getAdminDlBenchmarks() {
  return request('/api/admin/dl-benchmarks');
}

export function getImageUrl(path) {
  if (!path) return '';
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  if (path.startsWith('/')) return `${API_BASE}${path}`;
  return `${API_BASE}/${path}`;
}
