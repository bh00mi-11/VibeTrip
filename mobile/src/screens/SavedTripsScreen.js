import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator } from 'react-native';
import { THEME } from '../theme';
import { getMyTrips } from '../api';
import { Ionicons } from '@expo/vector-icons';

export default function SavedTripsScreen({ user, onOpenAuth, onSelectDestination }) {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    if (user) loadTrips();
    else setLoading(false);
  }, [user]);

  const loadTrips = async () => {
    try {
      setLoading(true);
      const res = await getMyTrips();
      setTrips(res.trips || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="bookmark-outline" size={48} color={THEME.colors.textMuted} />
        <Text style={styles.title}>Saved Itineraries</Text>
        <Text style={styles.sub}>Log in to access your saved trips across all devices.</Text>
        <TouchableOpacity style={styles.loginBtn} onPress={() => onOpenAuth('login')}>
          <Text style={styles.loginBtnText}>Sign In</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Saved Trips</Text>
        <Text style={styles.headerSub}>AI-generated itineraries & daily schedules</Text>
      </View>

      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator color={THEME.colors.primary} size="large" />
        </View>
      ) : trips.length === 0 ? (
        <View style={styles.centerContainer}>
          <Ionicons name="map-outline" size={42} color={THEME.colors.textMuted} />
          <Text style={styles.emptyTitle}>No trips saved yet</Text>
          <Text style={styles.emptySub}>Explore destinations and click "Save Trip" to keep them here.</Text>
        </View>
      ) : (
        <FlatList
          data={trips}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => {
            const isExpanded = expandedId === item.id;
            const days = item.itinerary?.days || [];

            return (
              <View style={styles.card}>
                <View style={styles.cardTop}>
                  <View>
                    <TouchableOpacity onPress={() => onSelectDestination(item.destination)}>
                      <Text style={styles.destName}>{item.destination}</Text>
                    </TouchableOpacity>
                    <Text style={styles.savedDate}>Saved {item.created_at}</Text>
                  </View>
                  <View style={styles.daysBadge}>
                    <Text style={styles.daysBadgeText}>{days.length} Days</Text>
                  </View>
                </View>

                <TouchableOpacity
                  style={styles.toggleBtn}
                  onPress={() => setExpandedId(isExpanded ? null : item.id)}
                >
                  <Text style={styles.toggleBtnText}>{isExpanded ? 'Hide Schedule' : 'View Day Schedule'}</Text>
                  <Ionicons name={isExpanded ? 'chevron-up' : 'chevron-down'} size={14} color={THEME.colors.primary} />
                </TouchableOpacity>

                {isExpanded && (
                  <View style={styles.scheduleList}>
                    {days.map((d) => (
                      <View key={d.day_number} style={styles.dayBox}>
                        <Text style={styles.dayTitle}>Day {d.day_number}: {d.theme}</Text>
                        <Text style={styles.periodText}>• Morning: {d.morning?.title}</Text>
                        <Text style={styles.periodText}>• Afternoon: {d.afternoon?.title}</Text>
                        <Text style={styles.periodText}>• Evening: {d.evening?.title}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </View>
            );
          }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: THEME.colors.bgDark },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 30, backgroundColor: THEME.colors.bgDark },
  header: { padding: 16, borderBottomWidth: 1, borderBottomColor: THEME.colors.border },
  headerTitle: { color: '#fff', fontSize: 20, fontWeight: '800' },
  headerSub: { color: THEME.colors.textMuted, fontSize: 12, marginTop: 2 },
  title: { color: '#fff', fontSize: 18, fontWeight: '700', marginTop: 12 },
  sub: { color: THEME.colors.textSecondary, fontSize: 13, textAlign: 'center', marginTop: 6, marginBottom: 18 },
  emptyTitle: { color: '#fff', fontSize: 16, fontWeight: '700', marginTop: 10 },
  emptySub: { color: THEME.colors.textMuted, fontSize: 12, textAlign: 'center', marginTop: 4 },
  loginBtn: { backgroundColor: THEME.colors.primary, paddingHorizontal: 20, paddingVertical: 10, borderRadius: THEME.radius.sm },
  loginBtnText: { color: '#fff', fontWeight: '700', fontSize: 14 },
  list: { padding: 16 },
  card: { backgroundColor: THEME.colors.bgCard, borderRadius: THEME.radius.md, padding: 14, borderWidth: 1, borderColor: THEME.colors.border, marginBottom: 12 },
  cardTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  destName: { color: '#fff', fontSize: 17, fontWeight: '700' },
  savedDate: { color: THEME.colors.textMuted, fontSize: 11, marginTop: 2 },
  daysBadge: { backgroundColor: 'rgba(16,185,129,0.2)', paddingHorizontal: 8, paddingVertical: 4, borderRadius: THEME.radius.full },
  daysBadgeText: { color: THEME.colors.primary, fontSize: 11, fontWeight: '700' },
  toggleBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: 10, paddingTop: 8, borderTopWidth: 1, borderTopColor: THEME.colors.border },
  toggleBtnText: { color: THEME.colors.primary, fontSize: 12, fontWeight: '600' },
  scheduleList: { marginTop: 10, gap: 8 },
  dayBox: { backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 6, padding: 8 },
  dayTitle: { color: '#fff', fontSize: 12, fontWeight: '700', marginBottom: 4 },
  periodText: { color: THEME.colors.textSecondary, fontSize: 11, marginVertical: 1 },
});
