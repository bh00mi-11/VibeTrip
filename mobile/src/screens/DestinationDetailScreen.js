import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity, Image,
  ActivityIndicator, Alert, TextInput, Modal
} from 'react-native';
import { THEME } from '../theme';
import {
  getDestination, generateTripPlan, saveTrip, getLocalExperiences,
  getBuddies, sendBuddyRequest, getImageUrl
} from '../api';
import { Ionicons } from '@expo/vector-icons';

export default function DestinationDetailScreen({ destinationName, user, onBack, onOpenAuth }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [dest, setDest] = useState(null);
  const [loading, setLoading] = useState(true);

  // Plan state
  const [plan, setPlan] = useState(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState(1);
  const [savingTrip, setSavingTrip] = useState(false);

  // Places state
  const [places, setPlaces] = useState([]);
  const [placesLoading, setPlacesLoading] = useState(false);

  // Travelers state
  const [travelers, setTravelers] = useState([]);
  const [travelersLoading, setTravelersLoading] = useState(false);
  const [connectModalUser, setConnectModalUser] = useState(null);
  const [connectNote, setConnectNote] = useState('');

  useEffect(() => {
    loadDest();
  }, [destinationName]);

  useEffect(() => {
    if (activeTab === 'plan' && !plan && dest) loadPlan();
    if (activeTab === 'places' && dest) loadPlaces();
    if (activeTab === 'travelers' && dest) loadTravelers();
  }, [activeTab, dest]);

  const loadDest = async () => {
    try {
      setLoading(true);
      const data = await getDestination(destinationName);
      setDest(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

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
      await saveTrip(destinationName, plan);
      Alert.alert('Saved!', 'Trip saved to your profile.');
    } catch (err) {
      Alert.alert('Error', err.message || 'Failed to save trip');
    } finally {
      setSavingTrip(false);
    }
  };

  const loadPlaces = async () => {
    try {
      setPlacesLoading(true);
      const res = await getLocalExperiences(destinationName);
      setPlaces(res.experiences || []);
    } catch (err) {
      console.error(err);
    } finally {
      setPlacesLoading(false);
    }
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
      Alert.alert('Request Sent', `Connection request sent to ${connectModalUser.name}.`);
      setConnectModalUser(null);
      setConnectNote('');
    } catch (err) {
      Alert.alert('Error', err.message || 'Failed to send connection request');
    }
  };

  if (loading || !dest) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={THEME.colors.primary} />
        <Text style={styles.loadingText}>Loading {destinationName}...</Text>
      </View>
    );
  }

  const scores = dest.scores || {};
  const photos = dest.photos || [];

  return (
    <View style={styles.container}>
      {/* Top Bar with Back Button */}
      <View style={styles.topBar}>
        <TouchableOpacity style={styles.backBtn} onPress={onBack}>
          <Ionicons name="arrow-back" size={20} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.topBarTitle} numberOfLines={1}>{dest.name}</Text>
        <View style={{ width: 36 }} />
      </View>

      <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Hero Photo Banner */}
        <View style={styles.heroContainer}>
          <Image
            source={{ uri: getImageUrl(photos[0]?.url || `/images/${dest.name}/photo_01.jpg`) }}
            style={styles.heroImage}
            resizeMode="cover"
          />
          <View style={styles.heroOverlay} />

          <View style={styles.heroInfo}>
            <View style={styles.badgeRow}>
              {dest.category ? (
                <View style={styles.catBadge}>
                  <Text style={styles.catBadgeText}>{dest.category}</Text>
                </View>
              ) : null}
              {dest.is_ai_estimated && (
                <View style={styles.aiBadge}>
                  <Ionicons name="sparkles" size={10} color="#C084FC" />
                  <Text style={styles.aiBadgeText}>AI Estimated</Text>
                </View>
              )}
            </View>

            <Text style={styles.heroTitle}>{dest.name}</Text>
            {(dest.state || dest.region) && (
              <View style={styles.locRow}>
                <Ionicons name="location" size={13} color="rgba(255,255,255,0.8)" />
                <Text style={styles.locText}>{[dest.state, dest.region].filter(Boolean).join(', ')}</Text>
              </View>
            )}
          </View>
        </View>

        {/* Vibe Score Bar Pills */}
        <View style={styles.vibePills}>
          <View style={styles.vibePill}>
            <Text style={styles.pillLabel}>Nature</Text>
            <Text style={[styles.pillVal, { color: THEME.colors.vibeNature }]}>{Math.round(scores.nature || 0)}</Text>
          </View>
          <View style={styles.vibePill}>
            <Text style={styles.pillLabel}>Adventure</Text>
            <Text style={[styles.pillVal, { color: THEME.colors.vibeAdventure }]}>{Math.round(scores.adventure || 0)}</Text>
          </View>
          <View style={styles.vibePill}>
            <Text style={styles.pillLabel}>Peace</Text>
            <Text style={[styles.pillVal, { color: THEME.colors.vibePeacefulness }]}>{Math.round(scores.peacefulness || 0)}</Text>
          </View>
          <View style={styles.vibePill}>
            <Text style={styles.pillLabel}>Crowd</Text>
            <Text style={[styles.pillVal, { color: THEME.colors.vibeCrowd }]}>{Math.round(scores.crowd_match || 0)}</Text>
          </View>
          <View style={styles.vibePill}>
            <Text style={styles.pillLabel}>Visual</Text>
            <Text style={[styles.pillVal, { color: THEME.colors.vibeVisual }]}>{Math.round(scores.visual_atmosphere || 0)}</Text>
          </View>
        </View>

        {/* Segmented Tab Buttons */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tabScroll}>
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'plan', label: '3-Day Plan' },
            { id: 'places', label: 'Local Places' },
            { id: 'travelers', label: 'Travelers' },
          ].map((tab) => (
            <TouchableOpacity
              key={tab.id}
              style={[styles.tabBtn, activeTab === tab.id && styles.tabBtnActive]}
              onPress={() => setActiveTab(tab.id)}
            >
              <Text style={[styles.tabBtnText, activeTab === tab.id && styles.tabBtnTextActive]}>
                {tab.label}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* TAB 1: OVERVIEW */}
        {activeTab === 'overview' && (
          <View style={styles.tabContent}>
            <View style={styles.card}>
              <Text style={styles.cardTitle}>About {dest.name}</Text>
              <Text style={styles.descText}>
                {dest.description || 'A breathtaking destination in India offering authentic local culture and unique landscapes.'}
              </Text>

              <View style={styles.metaRow}>
                <View style={styles.metaItem}>
                  <Text style={styles.metaLabel}>Best Season</Text>
                  <Text style={styles.metaValue}>{dest.best_time_to_visit || 'Year Round'}</Text>
                </View>
                <View style={styles.metaItem}>
                  <Text style={styles.metaLabel}>Geo Coords</Text>
                  <Text style={styles.metaValue}>{dest.latitude ? `${dest.latitude.toFixed(2)}, ${dest.longitude.toFixed(2)}` : 'Verified'}</Text>
                </View>
              </View>
            </View>

            {dest.top_attractions ? (
              <View style={styles.card}>
                <Text style={styles.cardTitle}>Top Attractions</Text>
                <Text style={styles.descText}>{dest.top_attractions}</Text>
              </View>
            ) : null}

            {/* Photos carousel */}
            <View style={styles.card}>
              <Text style={styles.cardTitle}>Photos & Manifest ({photos.length})</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginTop: 8 }}>
                {photos.map((p, i) => (
                  <View key={i} style={styles.photoItem}>
                    <Image source={{ uri: getImageUrl(p.url) }} style={styles.photoImg} />
                    <Text style={styles.photoAttraction} numberOfLines={1}>{p.attraction || `Spot ${i + 1}`}</Text>
                    <Text style={styles.photoAuthor} numberOfLines={1}>{p.author || 'Wikimedia'} ({p.license || 'CC'})</Text>
                  </View>
                ))}
              </ScrollView>
            </View>
          </View>
        )}

        {/* TAB 2: 3-DAY PLAN */}
        {activeTab === 'plan' && (
          <View style={styles.tabContent}>
            <View style={styles.planHeader}>
              <View>
                <Text style={styles.cardTitle}>AI Day-wise Itinerary</Text>
                <Text style={styles.subText}>Personalized for 3 days</Text>
              </View>
              <TouchableOpacity
                style={styles.saveBtn}
                onPress={handleSaveTrip}
                disabled={savingTrip}
              >
                <Ionicons name="bookmark" size={14} color="#fff" />
                <Text style={styles.saveBtnText}>{savingTrip ? '...' : 'Save Trip'}</Text>
              </TouchableOpacity>
            </View>

            {planLoading ? (
              <ActivityIndicator color={THEME.colors.primary} style={{ marginTop: 20 }} />
            ) : plan ? (
              <>
                <View style={styles.daySelector}>
                  {(plan.days || []).map((d) => (
                    <TouchableOpacity
                      key={d.day_number}
                      style={[styles.dayChip, selectedDay === d.day_number && styles.dayChipActive]}
                      onPress={() => setSelectedDay(d.day_number)}
                    >
                      <Text style={[styles.dayChipText, selectedDay === d.day_number && styles.dayChipTextActive]}>
                        Day {d.day_number}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>

                {(() => {
                  const currentDay = (plan.days || []).find((d) => d.day_number === selectedDay) || plan.days?.[0];
                  if (!currentDay) return null;

                  return (
                    <View style={styles.scheduleList}>
                      <Text style={styles.dayThemeText}>{currentDay.theme}</Text>

                      {/* Morning */}
                      <View style={styles.scheduleCard}>
                        <View style={styles.periodBadgeMorning}>
                          <Text style={styles.periodBadgeText}>Morning</Text>
                        </View>
                        <Text style={styles.periodTitle}>{currentDay.morning?.title}</Text>
                        <Text style={styles.periodDesc}>{currentDay.morning?.description}</Text>
                        {currentDay.morning?.local_recommendation && (
                          <Text style={styles.periodRec}>Spot: {currentDay.morning.local_recommendation}</Text>
                        )}
                      </View>

                      {/* Afternoon */}
                      <View style={styles.scheduleCard}>
                        <View style={styles.periodBadgeAfternoon}>
                          <Text style={styles.periodBadgeText}>Afternoon</Text>
                        </View>
                        <Text style={styles.periodTitle}>{currentDay.afternoon?.title}</Text>
                        <Text style={styles.periodDesc}>{currentDay.afternoon?.description}</Text>
                        {currentDay.afternoon?.local_recommendation && (
                          <Text style={styles.periodRec}>Lunch: {currentDay.afternoon.local_recommendation}</Text>
                        )}
                      </View>

                      {/* Evening */}
                      <View style={styles.scheduleCard}>
                        <View style={styles.periodBadgeEvening}>
                          <Text style={styles.periodBadgeText}>Evening</Text>
                        </View>
                        <Text style={styles.periodTitle}>{currentDay.evening?.title}</Text>
                        <Text style={styles.periodDesc}>{currentDay.evening?.description}</Text>
                        {currentDay.evening?.local_recommendation && (
                          <Text style={styles.periodRec}>Cafe/Sunset: {currentDay.evening.local_recommendation}</Text>
                        )}
                      </View>
                    </View>
                  );
                })()}
              </>
            ) : (
              <TouchableOpacity style={styles.actionBtnLarge} onPress={loadPlan}>
                <Text style={styles.actionBtnLargeText}>Generate 3-Day Plan</Text>
              </TouchableOpacity>
            )}
          </View>
        )}

        {/* TAB 3: LOCAL PLACES */}
        {activeTab === 'places' && (
          <View style={styles.tabContent}>
            {placesLoading ? (
              <ActivityIndicator color={THEME.colors.primary} style={{ marginTop: 20 }} />
            ) : places.length === 0 ? (
              <View style={styles.card}>
                <Text style={styles.descText}>No places submitted yet.</Text>
              </View>
            ) : (
              places.map((p) => (
                <View key={p.id} style={styles.placeCard}>
                  <View style={styles.placeHeader}>
                    <Text style={styles.placeName}>{p.name}</Text>
                    <View style={styles.sourcePill}>
                      <Text style={styles.sourcePillText}>{p.source_label}</Text>
                    </View>
                  </View>
                  <Text style={styles.placeCategory}>{p.category}</Text>
                  {p.description ? <Text style={styles.placeDesc}>{p.description}</Text> : null}
                  {p.contact_info ? <Text style={styles.placeContact}>Contact: {p.contact_info}</Text> : null}
                </View>
              ))
            )}
          </View>
        )}

        {/* TAB 4: TRAVELERS */}
        {activeTab === 'travelers' && (
          <View style={styles.tabContent}>
            {travelersLoading ? (
              <ActivityIndicator color={THEME.colors.primary} style={{ marginTop: 20 }} />
            ) : travelers.length === 0 ? (
              <View style={styles.card}>
                <Text style={styles.cardTitle}>No travelers found yet</Text>
                <Text style={styles.descText}>Be the first to post your dates for {dest.name}!</Text>
              </View>
            ) : (
              travelers.map((t) => (
                <View key={t.user_id} style={styles.travelerCard}>
                  <View style={styles.travelerHeader}>
                    <View>
                      <Text style={styles.travelerName}>{t.name}</Text>
                      <Text style={styles.travelerCity}>{t.home_city || 'Traveler'}</Text>
                    </View>
                    <View style={styles.matchPill}>
                      <Text style={styles.matchPillText}>{Math.round(t.compatibility_score || 0)}% Match</Text>
                    </View>
                  </View>

                  {t.bio ? <Text style={styles.travelerBio}>"{t.bio}"</Text> : null}

                  <TouchableOpacity
                    style={styles.connectBtn}
                    onPress={() => {
                      if (!user) onOpenAuth('login');
                      else setConnectModalUser(t);
                    }}
                  >
                    <Ionicons name="people" size={14} color="#fff" />
                    <Text style={styles.connectBtnText}>Connect & Share Contact</Text>
                  </TouchableOpacity>
                </View>
              ))
            )}
          </View>
        )}
      </ScrollView>

      {/* Connect Modal Sheet */}
      <Modal visible={!!connectModalUser} transparent animationType="slide">
        <View style={styles.modalBg}>
          <View style={styles.modalCard}>
            <Text style={styles.modalTitle}>Connect with {connectModalUser?.name}</Text>
            <Text style={styles.modalSub}>
              Send a note. Contact info is only shared after mutual acceptance.
            </Text>

            <TextInput
              style={styles.modalInput}
              multiline
              numberOfLines={3}
              placeholder="Hi! I'm planning to travel to this spot around the same time..."
              placeholderTextColor={THEME.colors.textMuted}
              value={connectNote}
              onChangeText={setConnectNote}
            />

            <View style={styles.modalActions}>
              <TouchableOpacity style={styles.modalCancel} onPress={() => setConnectModalUser(null)}>
                <Text style={styles.modalCancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.modalSubmit} onPress={handleSendRequest}>
                <Text style={styles.modalSubmitText}>Send Request</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: THEME.colors.bgDark },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: THEME.colors.bgDark },
  loadingText: { color: THEME.colors.textSecondary, marginTop: 12, fontSize: 13 },
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: THEME.colors.border,
  },
  backBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: THEME.colors.bgElevated,
    justifyContent: 'center',
    alignItems: 'center',
  },
  topBarTitle: { color: '#fff', fontSize: 16, fontWeight: '700', flex: 1, textAlign: 'center' },
  scroll: { flex: 1 },
  heroContainer: { height: 240, width: '100%', position: 'relative' },
  heroImage: { width: '100%', height: '100%' },
  heroOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(9, 13, 22, 0.6)' },
  heroInfo: { position: 'absolute', bottom: 16, left: 16, right: 16 },
  badgeRow: { flexDirection: 'row', gap: 6, marginBottom: 6 },
  catBadge: { backgroundColor: 'rgba(0,0,0,0.6)', paddingHorizontal: 8, paddingVertical: 4, borderRadius: THEME.radius.full },
  catBadgeText: { color: '#fff', fontSize: 10, fontWeight: '700' },
  aiBadge: { backgroundColor: 'rgba(168,85,247,0.3)', paddingHorizontal: 8, paddingVertical: 4, borderRadius: THEME.radius.full, flexDirection: 'row', alignItems: 'center', gap: 3 },
  aiBadgeText: { color: '#C084FC', fontSize: 10, fontWeight: '700' },
  heroTitle: { color: '#fff', fontSize: 26, fontWeight: '800' },
  locRow: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 4 },
  locText: { color: 'rgba(255,255,255,0.85)', fontSize: 13 },
  vibePills: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: THEME.colors.bgCard,
    paddingVertical: 10,
    marginHorizontal: 16,
    marginTop: 12,
    borderRadius: THEME.radius.md,
    borderWidth: 1,
    borderColor: THEME.colors.border,
  },
  vibePill: { alignItems: 'center' },
  pillLabel: { color: THEME.colors.textMuted, fontSize: 10 },
  pillVal: { fontSize: 13, fontWeight: '800', marginTop: 2 },
  tabScroll: { marginHorizontal: 16, marginVertical: 14 },
  tabBtn: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: THEME.radius.md,
    backgroundColor: 'rgba(255,255,255,0.04)',
    marginRight: 8,
    borderWidth: 1,
    borderColor: THEME.colors.border,
  },
  tabBtnActive: { backgroundColor: 'rgba(16,185,129,0.2)', borderColor: THEME.colors.primary },
  tabBtnText: { color: THEME.colors.textSecondary, fontSize: 13, fontWeight: '600' },
  tabBtnTextActive: { color: '#fff', fontWeight: '700' },
  tabContent: { paddingHorizontal: 16, paddingBottom: 60 },
  card: {
    backgroundColor: THEME.colors.bgCard,
    borderRadius: THEME.radius.md,
    padding: 16,
    borderWidth: 1,
    borderColor: THEME.colors.border,
    marginBottom: 14,
  },
  cardTitle: { color: '#fff', fontSize: 16, fontWeight: '700', marginBottom: 8 },
  descText: { color: THEME.colors.textSecondary, fontSize: 13, lineHeight: 19 },
  metaRow: { flexDirection: 'row', borderTopWidth: 1, borderTopColor: THEME.colors.border, paddingTop: 12, marginTop: 12 },
  metaItem: { flex: 1 },
  metaLabel: { color: THEME.colors.textMuted, fontSize: 11 },
  metaValue: { color: '#fff', fontSize: 13, fontWeight: '600', marginTop: 2 },
  photoItem: { width: 140, marginRight: 10, borderRadius: THEME.radius.sm, overflow: 'hidden', backgroundColor: '#1E293B' },
  photoImg: { width: '100%', height: 95 },
  photoAttraction: { color: '#fff', fontSize: 11, fontWeight: '600', paddingHorizontal: 6, paddingTop: 4 },
  photoAuthor: { color: THEME.colors.textMuted, fontSize: 9, paddingHorizontal: 6, paddingBottom: 6 },
  planHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  subText: { color: THEME.colors.textMuted, fontSize: 12 },
  saveBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: THEME.colors.primary,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: THEME.radius.sm,
  },
  saveBtnText: { color: '#fff', fontSize: 12, fontWeight: '700' },
  daySelector: { flexDirection: 'row', gap: 8, marginBottom: 14 },
  dayChip: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    backgroundColor: THEME.colors.bgCard,
    borderRadius: THEME.radius.sm,
    borderWidth: 1,
    borderColor: THEME.colors.border,
  },
  dayChipActive: { backgroundColor: THEME.colors.primary, borderColor: THEME.colors.primary },
  dayChipText: { color: THEME.colors.textSecondary, fontSize: 12, fontWeight: '600' },
  dayChipTextActive: { color: '#fff', fontWeight: '800' },
  scheduleList: { gap: 10 },
  dayThemeText: { color: THEME.colors.primary, fontSize: 14, fontWeight: '700', marginBottom: 6 },
  scheduleCard: {
    backgroundColor: THEME.colors.bgCard,
    borderRadius: THEME.radius.md,
    padding: 14,
    borderWidth: 1,
    borderColor: THEME.colors.border,
  },
  periodBadgeMorning: { alignSelf: 'flex-start', backgroundColor: 'rgba(245,158,11,0.2)', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 4, marginBottom: 6 },
  periodBadgeAfternoon: { alignSelf: 'flex-start', backgroundColor: 'rgba(6,182,212,0.2)', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 4, marginBottom: 6 },
  periodBadgeEvening: { alignSelf: 'flex-start', backgroundColor: 'rgba(168,85,247,0.2)', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 4, marginBottom: 6 },
  periodBadgeText: { color: '#fff', fontSize: 10, fontWeight: '700' },
  periodTitle: { color: '#fff', fontSize: 14, fontWeight: '700', marginBottom: 4 },
  periodDesc: { color: THEME.colors.textSecondary, fontSize: 12, lineHeight: 17 },
  periodRec: { color: THEME.colors.primary, fontSize: 11, fontWeight: '600', marginTop: 6 },
  actionBtnLarge: { backgroundColor: THEME.colors.primary, padding: 14, borderRadius: THEME.radius.md, alignItems: 'center', marginTop: 10 },
  actionBtnLargeText: { color: '#fff', fontWeight: '700', fontSize: 14 },
  placeCard: {
    backgroundColor: THEME.colors.bgCard,
    borderRadius: THEME.radius.md,
    padding: 14,
    borderWidth: 1,
    borderColor: THEME.colors.border,
    marginBottom: 10,
  },
  placeHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  placeName: { color: '#fff', fontSize: 14, fontWeight: '700' },
  sourcePill: { backgroundColor: 'rgba(6,182,212,0.15)', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  sourcePillText: { color: '#22D3EE', fontSize: 10, fontWeight: '600' },
  placeCategory: { color: THEME.colors.primary, fontSize: 11, textTransform: 'capitalize', marginTop: 2, marginBottom: 4 },
  placeDesc: { color: THEME.colors.textSecondary, fontSize: 12, lineHeight: 16 },
  placeContact: { color: THEME.colors.textMuted, fontSize: 10, marginTop: 4 },
  travelerCard: {
    backgroundColor: THEME.colors.bgCard,
    borderRadius: THEME.radius.md,
    padding: 14,
    borderWidth: 1,
    borderColor: THEME.colors.border,
    marginBottom: 12,
  },
  travelerHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  travelerName: { color: '#fff', fontSize: 15, fontWeight: '700' },
  travelerCity: { color: THEME.colors.textMuted, fontSize: 11, marginTop: 2 },
  matchPill: { backgroundColor: 'rgba(16,185,129,0.2)', paddingHorizontal: 8, paddingVertical: 4, borderRadius: THEME.radius.full },
  matchPillText: { color: THEME.colors.primary, fontSize: 11, fontWeight: '800' },
  travelerBio: { color: THEME.colors.textSecondary, fontSize: 12, marginVertical: 8, fontStyle: 'italic' },
  connectBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    backgroundColor: 'rgba(16,185,129,0.15)',
    borderWidth: 1,
    borderColor: THEME.colors.primary,
    paddingVertical: 8,
    borderRadius: THEME.radius.sm,
    marginTop: 6,
  },
  connectBtnText: { color: THEME.colors.primary, fontSize: 12, fontWeight: '700' },
  modalBg: { flex: 1, backgroundColor: 'rgba(0,0,0,0.7)', justifyContent: 'flex-end' },
  modalCard: { backgroundColor: '#111827', borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 20 },
  modalTitle: { color: '#fff', fontSize: 17, fontWeight: '700' },
  modalSub: { color: THEME.colors.textMuted, fontSize: 12, marginTop: 4, marginBottom: 14 },
  modalInput: {
    backgroundColor: '#1E293B',
    borderRadius: 8,
    padding: 12,
    color: '#fff',
    fontSize: 13,
    minHeight: 80,
    textAlignVertical: 'top',
    marginBottom: 16,
  },
  modalActions: { flexDirection: 'row', justifyContent: 'flex-end', gap: 10 },
  modalCancel: { paddingHorizontal: 14, paddingVertical: 8 },
  modalCancelText: { color: THEME.colors.textSecondary, fontSize: 13 },
  modalSubmit: { backgroundColor: THEME.colors.primary, paddingHorizontal: 16, paddingVertical: 8, borderRadius: 8 },
  modalSubmitText: { color: '#fff', fontWeight: '700', fontSize: 13 },
});
