import React, { useState } from 'react';
import { View, Text, StyleSheet, Modal, TextInput, TouchableOpacity, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { THEME } from '../theme';
import { authLogin, authSignup } from '../api';
import { Ionicons } from '@expo/vector-icons';

const DEMO_ACCOUNTS = [
  { label: 'Demo Tourist', email: 'tourist.demo@vibetrip.com', pass: 'DemoTourist2026!', badge: 'Tourist', color: '#0284c7' },
  { label: "Rohan (Goa)", email: 'rohan.goa@vibetrip.com', pass: 'DemoLocal2026!', badge: 'Goa Host', color: '#059669' },
  { label: 'Sunita (Manali)', email: 'sunita.manali@vibetrip.com', pass: 'DemoLocal2026!', badge: 'Manali Guide', color: '#7c3aed' },
  { label: 'Vikram (Rishikesh)', email: 'vikram.rishikesh@vibetrip.com', pass: 'DemoLocal2026!', badge: 'Rishikesh Host', color: '#ea580c' },
  { label: 'Demo Admin', email: 'admin@vibetrip.internal', pass: 'AdminSuperPass2026!', badge: 'Admin Portal', color: '#dc2626' }
];

export default function AuthModal({ visible, initialTab = 'login', onClose, onSuccess }) {
  const [tab, setTab] = useState(initialTab);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('tourist');
  const [homeCity, setHomeCity] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInstantDemo = async (acc) => {
    setEmail(acc.email);
    setPassword(acc.pass);
    setTab('login');
    try {
      setLoading(true);
      const res = await authLogin(acc.email, acc.pass);
      onSuccess(res.user);
      onClose();
    } catch (err) {
      Alert.alert('Demo Login Error', err.message || 'Could not connect to backend server. Make sure your phone is on the same Wi-Fi.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Required', 'Please enter email and password.');
      return;
    }

    try {
      setLoading(true);
      if (tab === 'login') {
        const res = await authLogin(email, password);
        onSuccess(res.user);
        onClose();
      } else {
        if (!name.trim()) {
          Alert.alert('Required', 'Please enter your name.');
          return;
        }
        const res = await authSignup({
          email,
          password,
          name,
          role,
          home_city: homeCity,
        });
        onSuccess(res.user);
        onClose();
      }
    } catch (err) {
      Alert.alert('Auth Failed', err.message || 'Check your credentials and connection to host.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.modalBg}>
        <View style={styles.modalCard}>
          <View style={styles.header}>
            <View>
              <Text style={styles.title}>{tab === 'login' ? 'Sign In to VibeTrip' : 'Create Account'}</Text>
              <Text style={styles.subtitle}>Multi-Modal AI Travel & Buddy Match</Text>
            </View>
            <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
              <Ionicons name="close" size={20} color={THEME.colors.textSecondary} />
            </TouchableOpacity>
          </View>

          {/* 1-Click Demo Accounts Row */}
          <View style={styles.demoSection}>
            <Text style={styles.demoSectionTitle}>⚡ 1-Click Instant Demo Logins:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.demoScroll}>
              {DEMO_ACCOUNTS.map((acc) => (
                <TouchableOpacity
                  key={acc.email}
                  style={[styles.demoCard, { borderLeftColor: acc.color }]}
                  onPress={() => handleInstantDemo(acc)}
                  disabled={loading}
                >
                  <Text style={styles.demoCardLabel}>{acc.label}</Text>
                  <Text style={styles.demoCardBadge}>{acc.badge}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>

          {/* Tab switcher */}
          <View style={styles.tabBar}>
            <TouchableOpacity
              style={[styles.tabBtn, tab === 'login' && styles.tabBtnActive]}
              onPress={() => setTab('login')}
            >
              <Text style={[styles.tabBtnText, tab === 'login' && styles.tabBtnTextActive]}>Log In</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.tabBtn, tab === 'signup' && styles.tabBtnActive]}
              onPress={() => setTab('signup')}
            >
              <Text style={[styles.tabBtnText, tab === 'signup' && styles.tabBtnTextActive]}>Sign Up</Text>
            </TouchableOpacity>
          </View>

          {tab === 'signup' && (
            <>
              <Text style={styles.label}>Full Name *</Text>
              <TextInput
                style={styles.input}
                placeholder="e.g. Priya Sharma"
                placeholderTextColor={THEME.colors.textMuted}
                value={name}
                onChangeText={setName}
              />

              <Text style={styles.label}>I am joining as</Text>
              <View style={styles.roleRow}>
                <TouchableOpacity
                  style={[styles.roleChip, role === 'tourist' && styles.roleChipActive]}
                  onPress={() => setRole('tourist')}
                >
                  <Text style={[styles.roleChipText, role === 'tourist' && styles.roleChipTextActive]}>
                    Tourist
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.roleChip, role === 'local' && styles.roleChipActive]}
                  onPress={() => setRole('local')}
                >
                  <Text style={[styles.roleChipText, role === 'local' && styles.roleChipTextActive]}>
                    Local Host
                  </Text>
                </TouchableOpacity>
              </View>

              <Text style={styles.label}>Home City</Text>
              <TextInput
                style={styles.input}
                placeholder="e.g. Bangalore, Mumbai"
                placeholderTextColor={THEME.colors.textMuted}
                value={homeCity}
                onChangeText={setHomeCity}
              />
            </>
          )}

          <Text style={styles.label}>Email Address *</Text>
          <TextInput
            style={styles.input}
            placeholder="you@example.com"
            placeholderTextColor={THEME.colors.textMuted}
            keyboardType="email-address"
            autoCapitalize="none"
            value={email}
            onChangeText={setEmail}
          />

          <Text style={styles.label}>Password (min 8 chars) *</Text>
          <TextInput
            style={styles.input}
            placeholder="••••••••"
            placeholderTextColor={THEME.colors.textMuted}
            secureTextEntry
            value={password}
            onChangeText={setPassword}
          />

          <TouchableOpacity style={styles.submitBtn} onPress={handleSubmit} disabled={loading}>
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.submitBtnText}>{tab === 'login' ? 'Sign In' : 'Join VibeTrip'}</Text>
            )}
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalBg: { flex: 1, backgroundColor: 'rgba(15, 23, 42, 0.65)', justifyContent: 'flex-end' },
  modalCard: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    maxHeight: '90%',
  },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  title: { color: THEME.colors.textMain, fontSize: 18, fontWeight: '800' },
  subtitle: { color: THEME.colors.textSecondary, fontSize: 12, marginTop: 2 },
  closeBtn: { padding: 6, backgroundColor: THEME.colors.bgElevated, borderRadius: 20 },
  
  demoSection: { backgroundColor: '#F0F9FF', padding: 10, borderRadius: 12, marginBottom: 14, borderWidth: 1, borderColor: '#BAE6FD' },
  demoSectionTitle: { fontSize: 12, fontWeight: '700', color: '#0369A1', marginBottom: 6 },
  demoScroll: { flexDirection: 'row' },
  demoCard: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 8,
    marginRight: 8,
    borderLeftWidth: 3,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  demoCardLabel: { fontSize: 11, fontWeight: '700', color: THEME.colors.textMain },
  demoCardBadge: { fontSize: 9, color: THEME.colors.textSecondary, marginTop: 1 },

  tabBar: { flexDirection: 'row', gap: 8, marginBottom: 12, borderBottomWidth: 1, borderBottomColor: THEME.colors.border, paddingBottom: 6 },
  tabBtn: { paddingVertical: 6, paddingHorizontal: 14, borderRadius: 8 },
  tabBtnActive: { backgroundColor: '#E0F2FE' },
  tabBtnText: { color: THEME.colors.textSecondary, fontSize: 13, fontWeight: '600' },
  tabBtnTextActive: { color: THEME.colors.primary, fontWeight: '800' },

  label: { color: THEME.colors.textSecondary, fontSize: 12, fontWeight: '600', marginBottom: 4, marginTop: 8 },
  input: {
    backgroundColor: '#F8FAFC',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 9,
    color: THEME.colors.textMain,
    fontSize: 13,
    borderWidth: 1,
    borderColor: THEME.colors.border
  },
  roleRow: { flexDirection: 'row', gap: 8, marginBottom: 4 },
  roleChip: { flex: 1, paddingVertical: 8, alignItems: 'center', backgroundColor: '#F8FAFC', borderRadius: 8, borderWidth: 1, borderColor: THEME.colors.border },
  roleChipActive: { backgroundColor: THEME.colors.primary, borderColor: THEME.colors.primary },
  roleChipText: { color: THEME.colors.textSecondary, fontSize: 11, fontWeight: '600' },
  roleChipTextActive: { color: '#FFFFFF', fontWeight: '800' },

  submitBtn: {
    backgroundColor: THEME.colors.primary,
    borderRadius: 10,
    paddingVertical: 13,
    alignItems: 'center',
    marginTop: 16,
    shadowColor: THEME.colors.primary,
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.25,
    shadowRadius: 6,
    elevation: 3,
  },
  submitBtnText: { color: '#FFFFFF', fontWeight: '800', fontSize: 14 },
});
