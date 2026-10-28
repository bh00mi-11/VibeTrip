import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { THEME } from '../theme';
import { submitContributePlace, getMySubmissions } from '../api';
import { Ionicons } from '@expo/vector-icons';

export default function ContributeScreen({ user, onOpenAuth }) {
  const [destination, setDestination] = useState('');
  const [category, setCategory] = useState('viewpoint');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [address, setAddress] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) loadMySubmissions();
  }, [user]);

  const loadMySubmissions = async () => {
    try {
      setLoading(true);
      const res = await getMySubmissions();
      setSubmissions(res.submissions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!destination.trim() || !name.trim() || !description.trim()) {
      Alert.alert('Required Fields', 'Please fill in destination, name, and description.');
      return;
    }

    try {
      setSubmitting(true);
      await submitContributePlace({
        destination,
        category,
        name,
        description,
        address,
      });
      Alert.alert('Submitted!', 'Your spot has been sent for admin review.');
      setDestination('');
      setName('');
      setDescription('');
      setAddress('');
      loadMySubmissions();
    } catch (err) {
      Alert.alert('Error', err.message || 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (!user) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="add-circle-outline" size={48} color={THEME.colors.textMuted} />
        <Text style={styles.title}>Submit Local Spots</Text>
        <Text style={styles.sub}>Log in to submit authentic viewpoints, cafes, and hidden gems.</Text>
        <TouchableOpacity style={styles.loginBtn} onPress={() => onOpenAuth('login')}>
          <Text style={styles.loginBtnText}>Sign In</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Contribute a Spot</Text>
        <Text style={styles.headerSub}>Help travelers discover authentic hidden gems</Text>
      </View>

      <View style={styles.formCard}>
        <Text style={styles.label}>Destination *</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. Shillong, Manali, Goa"
          placeholderTextColor={THEME.colors.textMuted}
          value={destination}
          onChangeText={setDestination}
        />

        <Text style={styles.label}>Category</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.catScroll}>
          {['viewpoint', 'cafe', 'food', 'attraction', 'activity'].map((cat) => (
            <TouchableOpacity
              key={cat}
              style={[styles.catChip, category === cat && styles.catChipActive]}
              onPress={() => setCategory(cat)}
            >
              <Text style={[styles.catChipText, category === cat && styles.catChipTextActive]}>
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        <Text style={styles.label}>Place Name *</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. Laitlum Canyon Sunrise Edge"
          placeholderTextColor={THEME.colors.textMuted}
          value={name}
          onChangeText={setName}
        />

        <Text style={styles.label}>Description & Insider Tips *</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          multiline
          numberOfLines={3}
          placeholder="What makes this place special? Best time to visit..."
          placeholderTextColor={THEME.colors.textMuted}
          value={description}
          onChangeText={setDescription}
        />

        <Text style={styles.label}>Address / Landmark (optional)</Text>
        <TextInput
          style={styles.input}
          placeholder="e.g. Near Police Bazar"
          placeholderTextColor={THEME.colors.textMuted}
          value={address}
          onChangeText={setAddress}
        />

        <TouchableOpacity style={styles.submitBtn} onPress={handleSubmit} disabled={submitting}>
          <Text style={styles.submitBtnText}>{submitting ? 'Submitting...' : 'Send for Review'}</Text>
        </TouchableOpacity>
      </View>

      {/* Track my submissions */}
      <View style={styles.subListSection}>
        <Text style={styles.sectionTitle}>My Past Submissions</Text>
        {loading ? (
          <ActivityIndicator color={THEME.colors.primary} style={{ marginTop: 10 }} />
        ) : submissions.length === 0 ? (
          <Text style={styles.emptyNote}>No submissions yet.</Text>
        ) : (
          submissions.map((s) => (
            <View key={s.id} style={styles.subCard}>
              <View style={styles.subCardTop}>
                <Text style={styles.subName}>{s.name}</Text>
                <View style={[
                  styles.statusBadge,
                  s.status === 'approved' ? { backgroundColor: 'rgba(16,185,129,0.2)' } :
                  s.status === 'rejected' ? { backgroundColor: 'rgba(239,68,68,0.2)' } :
                  { backgroundColor: 'rgba(245,158,11,0.2)' }
                ]}>
                  <Text style={[
                    styles.statusText,
                    s.status === 'approved' ? { color: THEME.colors.primary } :
                    s.status === 'rejected' ? { color: THEME.colors.danger } :
                    { color: THEME.colors.warning }
                  ]}>
                    {s.status.toUpperCase()}
                  </Text>
                </View>
              </View>
              <Text style={styles.subDest}>{s.destination} • {s.category}</Text>
            </View>
          ))
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: THEME.colors.bgDark },
  content: { padding: 16, paddingBottom: 60 },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 30, backgroundColor: THEME.colors.bgDark },
  header: { marginBottom: 16 },
  headerTitle: { color: '#fff', fontSize: 20, fontWeight: '800' },
  headerSub: { color: THEME.colors.textMuted, fontSize: 12, marginTop: 2 },
  title: { color: '#fff', fontSize: 18, fontWeight: '700', marginTop: 12 },
  sub: { color: THEME.colors.textSecondary, fontSize: 13, textAlign: 'center', marginTop: 6, marginBottom: 18 },
  loginBtn: { backgroundColor: THEME.colors.primary, paddingHorizontal: 20, paddingVertical: 10, borderRadius: THEME.radius.sm },
  loginBtnText: { color: '#fff', fontWeight: '700', fontSize: 14 },
  formCard: { backgroundColor: THEME.colors.bgCard, borderRadius: THEME.radius.md, padding: 16, borderWidth: 1, borderColor: THEME.colors.border },
  label: { color: THEME.colors.textSecondary, fontSize: 12, fontWeight: '600', marginBottom: 4, marginTop: 10 },
  input: { backgroundColor: THEME.colors.bgElevated, borderRadius: THEME.radius.sm, paddingHorizontal: 12, paddingVertical: 8, color: '#fff', fontSize: 13, borderWidth: 1, borderColor: THEME.colors.border },
  textArea: { minHeight: 70, textAlignVertical: 'top' },
  catScroll: { marginBottom: 4 },
  catChip: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: THEME.radius.full, backgroundColor: 'rgba(255,255,255,0.06)', marginRight: 6 },
  catChipActive: { backgroundColor: THEME.colors.primary },
  catChipText: { color: THEME.colors.textSecondary, fontSize: 11, fontWeight: '600' },
  catChipTextActive: { color: '#fff', fontWeight: '700' },
  submitBtn: { backgroundColor: THEME.colors.primary, borderRadius: THEME.radius.sm, paddingVertical: 12, alignItems: 'center', marginTop: 16 },
  submitBtnText: { color: '#fff', fontWeight: '700', fontSize: 14 },
  subListSection: { marginTop: 24 },
  sectionTitle: { color: '#fff', fontSize: 16, fontWeight: '700', marginBottom: 10 },
  emptyNote: { color: THEME.colors.textMuted, fontSize: 12 },
  subCard: { backgroundColor: THEME.colors.bgCard, borderRadius: THEME.radius.sm, padding: 12, marginBottom: 8, borderWidth: 1, borderColor: THEME.colors.border },
  subCardTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  subName: { color: '#fff', fontSize: 14, fontWeight: '600' },
  statusBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 4 },
  statusText: { fontSize: 10, fontWeight: '700' },
  subDest: { color: THEME.colors.textMuted, fontSize: 11, marginTop: 2 },
});
