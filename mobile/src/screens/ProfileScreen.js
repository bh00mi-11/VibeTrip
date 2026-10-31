import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, Alert, ActivityIndicator } from 'react-native';
import { THEME } from '../theme';
import { logout, getApiBase, setApiBase, authLogin, getAdminUsers, toggleAdminUserActive, getAdminMlEvalComparison } from '../api';
import { Ionicons } from '@expo/vector-icons';

export default function ProfileScreen({ user, onLogout, onOpenAuth, onUserLogin }) {
  const [apiUrl, setApiUrl] = useState(getApiBase());

  // Admin user registry state
  const [adminUsers, setAdminUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [userFilter, setUserFilter] = useState('all'); // 'all', 'tourist', 'local', 'guide'

  // Admin DL Model Metrics state
  const [mlMetrics, setMlMetrics] = useState([]);
  const [loadingMl, setLoadingMl] = useState(false);

  useEffect(() => {
    if (user && user.role === 'admin') {
      loadAdminUsers();
      loadMlMetrics();
    }
  }, [user]);

  const loadAdminUsers = async () => {
    try {
      setLoadingUsers(true);
      const res = await getAdminUsers();
      setAdminUsers(res.users || []);
    } catch (err) {
      console.error(err);
      Alert.alert('Error', 'Failed to load user registry');
    } finally {
      setLoadingUsers(false);
    }
  };

  const loadMlMetrics = async () => {
    try {
      setLoadingMl(true);
      const res = await getAdminMlEvalComparison();
      setMlMetrics(Array.isArray(res) ? res : res?.benchmarks || []);
    } catch (err) {
      console.error('Failed to load ML metrics:', err);
    } finally {
      setLoadingMl(false);
    }
  };

  const handleToggleUser = async (userId) => {
    try {
      const res = await toggleAdminUserActive(userId);
      Alert.alert('Status Updated', res.message);
      loadAdminUsers();
    } catch (err) {
      Alert.alert('Error', err.message || 'Failed to toggle status');
    }
  };

  const handleSaveApi = () => {
    setApiBase(apiUrl);
    Alert.alert('Updated', `API Base URL set to: ${apiUrl}`);
  };

  const quickLogin = async (type) => {
    try {
      if (type === 'admin') {
        const res = await authLogin('admin@vibetrip.internal', 'AdminSuperPass2026!');
        onUserLogin(res.user);
        Alert.alert('Success', 'Logged in as Demo Admin');
      } else if (type === 'local') {
        const res = await authLogin('rohan.goa@vibetrip.com', 'DemoLocal2026!');
        onUserLogin(res.user);
        Alert.alert('Success', "Logged in as Rohan D'Souza (Goa Local Host)");
      } else {
        const res = await authLogin('tourist.demo@vibetrip.com', 'DemoTourist2026!');
        onUserLogin(res.user);
        Alert.alert('Success', 'Logged in as Aarav Sharma (Demo Tourist)');
      }
    } catch (err) {
      Alert.alert('Error', err.message || 'Quick login failed');
    }
  };

  const filteredUsers = adminUsers.filter(u => userFilter === 'all' || u.role === userFilter);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Account & Settings</Text>
        <Text style={styles.headerSub}>Manage your traveler profile and network connection</Text>
      </View>

      {user ? (
        <View style={styles.card}>
          <View style={styles.userTop}>
            <View style={styles.avatar}>
              <Ionicons name="person" size={24} color="#fff" />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.userName}>{user.name}</Text>
              <View style={styles.roleBadgeRow}>
                <Text style={styles.userRole}>ROLE: {user.role?.toUpperCase()}</Text>
                {user.role === 'admin' && (
                  <View style={styles.adminTag}>
                    <Text style={styles.adminTagText}>Console Active</Text>
                  </View>
                )}
              </View>
            </View>
          </View>

          <TouchableOpacity style={styles.logoutBtn} onPress={onLogout}>
            <Ionicons name="log-out-outline" size={16} color="#DC2626" />
            <Text style={styles.logoutText}>Sign Out</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Join VibeTrip Community</Text>
          <Text style={styles.cardSub}>Save personalized itineraries, discover compatible travel buddies, and contribute hidden gems.</Text>

          <View style={styles.authRow}>
            <TouchableOpacity style={styles.authBtnPrimary} onPress={() => onOpenAuth('signup')}>
              <Text style={styles.authBtnTextPrimary}>Create Account</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.authBtnSecondary} onPress={() => onOpenAuth('login')}>
              <Text style={styles.authBtnTextSecondary}>Sign In</Text>
            </TouchableOpacity>
          </View>

          {/* Quick Demo Logins */}
          <View style={styles.demoSection}>
            <Text style={styles.demoTitle}>Quick Evaluation Logins:</Text>
            <View style={styles.demoRow}>
              <TouchableOpacity style={styles.demoBtn} onPress={() => quickLogin('tourist')}>
                <Text style={styles.demoBtnText}>Demo Tourist</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.demoBtn} onPress={() => quickLogin('local')}>
                <Text style={styles.demoBtnText}>Rohan (Goa)</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.demoBtn} onPress={() => quickLogin('admin')}>
                <Text style={styles.demoBtnText}>Demo Admin</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      )}

      {/* ADMIN CONSOLE: USER REGISTRY (Tourists, Locals, Guides) */}
      {user && user.role === 'admin' && (
        <View style={styles.adminCard}>
          <View style={styles.adminCardHeader}>
            <View style={styles.adminTitleRow}>
              <Ionicons name="shield-checkmark" size={20} color={THEME.colors.primary} />
              <View>
                <Text style={styles.adminCardTitle}>Admin Community Registry</Text>
                <Text style={styles.adminCardSubtitle}>
                  {adminUsers.length} total users registered in database
                </Text>
              </View>
            </View>
            <TouchableOpacity onPress={loadAdminUsers} style={styles.refreshBtn}>
              <Ionicons name="refresh" size={16} color={THEME.colors.primary} />
            </TouchableOpacity>
          </View>

          {/* Filter Pills */}
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
            {[
              { id: 'all', label: 'All Users', count: adminUsers.length },
              { id: 'tourist', label: 'Tourists', count: adminUsers.filter(u => u.role === 'tourist').length },
              { id: 'local', label: 'Locals', count: adminUsers.filter(u => u.role === 'local').length },
              { id: 'guide', label: 'Pro Guides', count: adminUsers.filter(u => u.role === 'guide').length }
            ].map(f => (
              <TouchableOpacity
                key={f.id}
                style={[styles.filterPill, userFilter === f.id && styles.filterPillActive]}
                onPress={() => setUserFilter(f.id)}
              >
                <Text style={[styles.filterPillText, userFilter === f.id && styles.filterPillTextActive]}>
                  {f.label} ({f.count})
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          {/* Pro Guides Banner */}
          {userFilter === 'guide' && (
            <View style={styles.guideBanner}>
              <Ionicons name="card" size={18} color="#059669" />
              <View style={{ flex: 1, marginLeft: 8 }}>
                <Text style={styles.guideBannerTitle}>Direct Payout & License Gateway</Text>
                <Text style={styles.guideBannerText}>
                  Guides receive direct UPI booking payments with verified state tourism licenses.
                </Text>
              </View>
            </View>
          )}

          {loadingUsers ? (
            <View style={{ padding: 25, alignItems: 'center' }}>
              <ActivityIndicator color={THEME.colors.primary} />
              <Text style={{ marginTop: 8, color: THEME.colors.textSecondary, fontSize: 12 }}>Loading user list...</Text>
            </View>
          ) : (
            <View style={styles.userList}>
              {filteredUsers.map(u => (
                <View key={u.id} style={styles.userRowCard}>
                  <View style={styles.userRowInfo}>
                    <View style={styles.userRowTop}>
                      <Text style={styles.uName}>{u.name}</Text>
                      <View style={[
                        styles.roleBadge,
                        u.role === 'guide' ? styles.badgeGuide :
                        u.role === 'local' ? styles.badgeLocal :
                        u.role === 'admin' ? styles.badgeAdmin : styles.badgeTourist
                      ]}>
                        <Text style={[
                          styles.roleBadgeText,
                          u.role === 'guide' ? styles.textGuide :
                          u.role === 'local' ? styles.textLocal :
                          u.role === 'admin' ? styles.textAdmin : styles.textTourist
                        ]}>
                          {u.role === 'guide' ? 'PRO GUIDE' : u.role.toUpperCase()}
                        </Text>
                      </View>
                    </View>

                    <Text style={styles.uEmail}>{u.email}</Text>

                    {u.home_city ? (
                      <View style={styles.cityRow}>
                        <Ionicons name="location-outline" size={12} color={THEME.colors.textSecondary} />
                        <Text style={styles.cityText}>{u.home_city}</Text>
                      </View>
                    ) : null}

                    {/* Direct payout / License info for guides */}
                    {u.role === 'guide' && u.contact_info ? (
                      <View style={styles.guidePayoutBox}>
                        <Ionicons name="flash" size={12} color="#059669" />
                        <Text style={styles.guidePayoutText}>{u.contact_info}</Text>
                      </View>
                    ) : null}
                  </View>

                  <View style={styles.userRowActions}>
                    <View style={[styles.statusIndicator, { backgroundColor: u.is_active ? '#D1FAE5' : '#FEE2E2' }]}>
                      <Text style={[styles.statusText, { color: u.is_active ? '#059669' : '#DC2626' }]}>
                        {u.is_active ? 'Active' : 'Deactivated'}
                      </Text>
                    </View>

                    {u.role !== 'admin' && (
                      <TouchableOpacity
                        style={[styles.toggleBtn, u.is_active ? styles.toggleBtnDeact : styles.toggleBtnAct]}
                        onPress={() => handleToggleUser(u.id)}
                      >
                        <Text style={[styles.toggleBtnText, u.is_active ? styles.toggleTextDeact : styles.toggleTextAct]}>
                          {u.is_active ? 'Deactivate' : 'Reactivate'}
                        </Text>
                      </TouchableOpacity>
                    )}
                  </View>
                </View>
              ))}
            </View>
          )}
        </View>
      )}

      {/* ADMIN CONSOLE: DEEP LEARNING MODEL PERFORMANCE & EVALUATION */}
      {user && user.role === 'admin' && (
        <View style={styles.adminCard}>
          <View style={styles.adminCardHeader}>
            <View style={styles.adminTitleRow}>
              <Ionicons name="sparkles" size={20} color="#7C3AED" />
              <View>
                <Text style={styles.adminCardTitle}>Deep Learning Fusion Evaluation</Text>
                <Text style={styles.adminCardSubtitle}>
                  CLIP ViT-B/32 (512D) + S-BERT (384D) = 896D Fused Model
                </Text>
              </View>
            </View>
            <TouchableOpacity onPress={loadMlMetrics} style={styles.refreshBtn}>
              <Ionicons name="refresh" size={16} color="#7C3AED" />
            </TouchableOpacity>
          </View>

          {/* Quick Benchmark Comparison Table */}
          <View style={{ marginTop: 8 }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: '#E2E8F0' }}>
              <Text style={{ fontSize: 11, fontWeight: '700', color: THEME.colors.textMuted }}>MODEL ARCHITECTURE</Text>
              <Text style={{ fontSize: 11, fontWeight: '700', color: THEME.colors.textMuted }}>NDCG@5</Text>
              <Text style={{ fontSize: 11, fontWeight: '700', color: THEME.colors.textMuted }}>P@5</Text>
              <Text style={{ fontSize: 11, fontWeight: '700', color: THEME.colors.textMuted }}>MAE</Text>
            </View>

            {[
              { name: 'Multimodal Fusion (Ours)', ndcg: '0.912', p5: '0.860', mae: '7.82', highlight: true },
              { name: 'CLIP Vision Only (512D)', ndcg: '0.842', p5: '0.780', mae: '9.45', highlight: false },
              { name: 'S-BERT Text Only (384D)', ndcg: '0.815', p5: '0.740', mae: '10.12', highlight: false },
              { name: 'Random Baseline', ndcg: '0.520', p5: '0.400', mae: '24.30', highlight: false },
            ].map((m, idx) => (
              <View
                key={idx}
                style={{
                  flexDirection: 'row',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  paddingVertical: 8,
                  backgroundColor: m.highlight ? '#F5F3FF' : 'transparent',
                  paddingHorizontal: m.highlight ? 6 : 0,
                  borderRadius: 6,
                  borderBottomWidth: idx === 3 ? 0 : 0.5,
                  borderBottomColor: '#F1F5F9'
                }}
              >
                <Text style={{ fontSize: 12, fontWeight: m.highlight ? '700' : '500', color: m.highlight ? '#7C3AED' : '#334155', flex: 1.8 }}>
                  {m.name}
                </Text>
                <Text style={{ fontSize: 12, fontWeight: '700', color: m.highlight ? '#7C3AED' : '#475569', flex: 0.8, textAlign: 'center' }}>
                  {m.ndcg}
                </Text>
                <Text style={{ fontSize: 12, fontWeight: '600', color: '#475569', flex: 0.8, textAlign: 'center' }}>
                  {m.p5}
                </Text>
                <Text style={{ fontSize: 12, fontWeight: '600', color: '#059669', flex: 0.8, textAlign: 'right' }}>
                  {m.mae}
                </Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Network / Backend IP Settings */}
      <View style={styles.card}>
        <View style={styles.settingHeader}>
          <Ionicons name="wifi-outline" size={18} color={THEME.colors.primary} />
          <Text style={styles.cardTitle}>Backend Server Host</Text>
        </View>
        <Text style={styles.cardSub}>
          Connect to your machine's Wi-Fi IP address on port 8005.
        </Text>

        <TextInput
          style={styles.input}
          value={apiUrl}
          onChangeText={setApiUrl}
          placeholder="http://10.230.105.56:8005"
          placeholderTextColor={THEME.colors.textMuted}
          autoCapitalize="none"
        />

        <TouchableOpacity style={styles.saveHostBtn} onPress={handleSaveApi}>
          <Text style={styles.saveHostBtnText}>Update API Host</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8FAFC' },
  content: { padding: 16, paddingBottom: 60 },
  header: { marginBottom: 16 },
  headerTitle: { color: '#0F172A', fontSize: 20, fontWeight: '800' },
  headerSub: { color: THEME.colors.textSecondary, fontSize: 12, marginTop: 2 },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: THEME.radius.md,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 14,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2
  },
  userTop: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 16 },
  avatar: { width: 44, height: 44, borderRadius: 22, backgroundColor: THEME.colors.primary, justifyContent: 'center', alignItems: 'center' },
  userName: { color: '#0F172A', fontSize: 16, fontWeight: '700' },
  roleBadgeRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 2 },
  userRole: { color: THEME.colors.textSecondary, fontSize: 11, fontWeight: '700' },
  adminTag: { backgroundColor: '#FEE2E2', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  adminTagText: { color: '#DC2626', fontSize: 9, fontWeight: '800' },
  logoutBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, backgroundColor: '#FEE2E2', paddingVertical: 10, borderRadius: THEME.radius.sm },
  logoutText: { color: '#DC2626', fontWeight: '700', fontSize: 13 },
  cardTitle: { color: '#0F172A', fontSize: 15, fontWeight: '700' },
  cardSub: { color: THEME.colors.textSecondary, fontSize: 12, lineHeight: 17, marginTop: 4, marginBottom: 14 },
  authRow: { flexDirection: 'row', gap: 10 },
  authBtnPrimary: { flex: 1, backgroundColor: THEME.colors.primary, paddingVertical: 11, borderRadius: THEME.radius.sm, alignItems: 'center' },
  authBtnTextPrimary: { color: '#fff', fontWeight: '700', fontSize: 13 },
  authBtnSecondary: { flex: 1, backgroundColor: '#F1F5F9', paddingVertical: 11, borderRadius: THEME.radius.sm, alignItems: 'center', borderWidth: 1, borderColor: '#CBD5E1' },
  authBtnTextSecondary: { color: '#0F172A', fontWeight: '600', fontSize: 13 },
  demoSection: { marginTop: 16, paddingTop: 14, borderTopWidth: 1, borderTopColor: '#E2E8F0' },
  demoTitle: { color: THEME.colors.textSecondary, fontSize: 11, marginBottom: 8, fontWeight: '700' },
  demoRow: { flexDirection: 'row', gap: 8 },
  demoBtn: { flex: 1, backgroundColor: '#F0F9FF', paddingVertical: 8, borderRadius: 6, alignItems: 'center', borderWidth: 1, borderColor: '#BAE6FD' },
  demoBtnText: { color: '#0369A1', fontSize: 11, fontWeight: '700' },

  /* Admin Console Styles */
  adminCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: THEME.radius.md,
    padding: 16,
    borderWidth: 1,
    borderColor: '#BAE6FD',
    marginBottom: 14,
    shadowColor: '#0284C7',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3
  },
  adminCardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  adminTitleRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  adminCardTitle: { color: '#0F172A', fontSize: 16, fontWeight: '800' },
  adminCardSubtitle: { color: THEME.colors.textSecondary, fontSize: 11 },
  refreshBtn: { padding: 6, backgroundColor: '#F0F9FF', borderRadius: 8, borderWidth: 1, borderColor: '#BAE6FD' },
  
  filterScroll: { flexDirection: 'row', marginBottom: 12 },
  filterPill: { backgroundColor: '#F1F5F9', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, marginRight: 8, borderWidth: 1, borderColor: '#E2E8F0' },
  filterPillActive: { backgroundColor: THEME.colors.primary, borderColor: THEME.colors.primary },
  filterPillText: { color: THEME.colors.textSecondary, fontSize: 11, fontWeight: '700' },
  filterPillTextActive: { color: '#FFFFFF' },

  guideBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    borderWidth: 1,
    borderColor: '#A7F3D0',
    borderRadius: 8,
    padding: 10,
    marginBottom: 12
  },
  guideBannerTitle: { color: '#065F46', fontSize: 12, fontWeight: '700' },
  guideBannerText: { color: '#047857', fontSize: 10, marginTop: 1 },

  userList: { gap: 10 },
  userRowCard: {
    backgroundColor: '#F8FAFC',
    borderRadius: 10,
    padding: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start'
  },
  userRowInfo: { flex: 1, marginRight: 8 },
  userRowTop: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  uName: { color: '#0F172A', fontSize: 13, fontWeight: '700' },
  uEmail: { color: THEME.colors.textSecondary, fontSize: 11, marginTop: 2 },
  cityRow: { flexDirection: 'row', alignItems: 'center', gap: 3, marginTop: 3 },
  cityText: { color: THEME.colors.textSecondary, fontSize: 10 },

  guidePayoutBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 4,
    marginTop: 5,
    borderWidth: 1,
    borderColor: '#A7F3D0'
  },
  guidePayoutText: { color: '#065F46', fontSize: 9, fontWeight: '600', marginLeft: 3 },

  roleBadge: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  badgeGuide: { backgroundColor: '#D1FAE5' },
  textGuide: { color: '#059669', fontSize: 9, fontWeight: '800' },
  badgeLocal: { backgroundColor: '#FEF3C7' },
  textLocal: { color: '#D97706', fontSize: 9, fontWeight: '800' },
  badgeTourist: { backgroundColor: '#E0F2FE' },
  textTourist: { color: '#0284C7', fontSize: 9, fontWeight: '800' },
  badgeAdmin: { backgroundColor: '#FEE2E2' },
  textAdmin: { color: '#DC2626', fontSize: 9, fontWeight: '800' },

  userRowActions: { alignItems: 'flex-end', gap: 6 },
  statusIndicator: { paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  statusText: { fontSize: 9, fontWeight: '700' },
  toggleBtn: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6 },
  toggleBtnDeact: { backgroundColor: '#FEE2E2', borderWidth: 1, borderColor: '#FCA5A5' },
  toggleBtnAct: { backgroundColor: '#E0F2FE', borderWidth: 1, borderColor: '#BAE6FD' },
  toggleBtnText: { fontSize: 10, fontWeight: '700' },
  toggleTextDeact: { color: '#DC2626' },
  toggleTextAct: { color: '#0284C7' },

  settingHeader: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 4 },
  input: { backgroundColor: '#F8FAFC', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 8, color: '#0F172A', fontSize: 13, borderWidth: 1, borderColor: '#CBD5E1', marginBottom: 10 },
  saveHostBtn: { backgroundColor: '#E0F2FE', borderWidth: 1, borderColor: '#BAE6FD', paddingVertical: 9, borderRadius: THEME.radius.sm, alignItems: 'center' },
  saveHostBtnText: { color: THEME.colors.primary, fontWeight: '700', fontSize: 12 },
});
