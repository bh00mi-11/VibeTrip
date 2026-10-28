// Default to your machine's LAN IP so physical phones running Expo Go connect immediately
let API_BASE = 'http://10.230.105.56:8005';
let authToken = null;
let currentUser = null;

export function getApiBase() {
  return API_BASE;
}

export function setApiBase(base) {
  API_BASE = base.replace(/\/+$/, '');
}

export function getToken() {
  return authToken;
}

export function setToken(token) {
  authToken = token;
}

export function getUser() {
  return currentUser;
}

export function setUser(user) {
  currentUser = user;
}

export function logout() {
  authToken = null;
  currentUser = null;
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const res = await fetch(url, {
    ...options,
    headers,
  });

  let data = null;
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
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

export async function generateTripPlan(destination, days = 3) {
  return request('/api/trip-plan', {
    method: 'POST',
    body: JSON.stringify({
      destination,
      days,
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

export async function getLocalExperiences(destination, category = null) {
  const q = category && category !== 'all' ? `?category=${category}` : '';
  return request(`/api/local-experiences/${encodeURIComponent(destination)}${q}`);
}

export async function getBuddies(destination) {
  return request(`/api/buddies/${encodeURIComponent(destination)}`);
}

export async function sendBuddyRequest(toUserId, destination, note = '') {
  return request('/api/buddy-requests/send', {
    method: 'POST',
    body: JSON.stringify({
      to_user_id: toUserId,
      destination,
      note,
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

export async function submitContributePlace(data) {
  return request('/api/contribute/submit', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getMySubmissions() {
  return request('/api/contribute/my');
}

export async function getAdminUsers() {
  return request('/api/admin/users');
}

export async function toggleAdminUserActive(userId) {
  return request(`/api/admin/users/${userId}/toggle-active`, { method: 'PATCH' });
}

export function getImageUrl(path) {
  if (!path) return 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&q=80';
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  if (path.startsWith('/')) return `${API_BASE}${path}`;
  return `${API_BASE}/${path}`;
}
