import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { THEME } from '../theme';
import { getReceivedBuddyRequests, getSentBuddyRequests, acceptBuddyRequest, declineBuddyRequest } from '../api';
import { Ionicons } from '@expo/vector-icons';

export default function InboxScreen({ user, onOpenAuth }) {
  const [activeTab, setActiveTab] = useState('received');
  const [received, setReceived] = useState([]);
  const [sent, setSent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) loadRequests();
    else setLoading(false);
  }, [user]);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const [rRes, sRes] = await Promise.all([
        getReceivedBuddyRequests(),
        getSentBuddyRequests(),
      ]);
      setReceived(rRes.received_requests || []);
      setSent(sRes.sent_requests || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (id) => {
    try {
      await acceptBuddyRequest(id);
      Alert.alert('Accepted', 'Connection confirmed. Contact info unlocked.');
      loadRequests();
    } catch (err) {
      Alert.alert('Error', err.message || 'Failed to accept request');
    }
  };

  const handleDecline = async (id) => {
    try {
      await declineBuddyRequest(id);
      loadRequests();
    } catch (err) {
      Alert.alert('Error', err.message || 'Failed to decline request');
    }
  };

  if (!user) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="mail-outline" size={48} color={THEME.colors.textMuted} />
        <Text style={styles.title}>Traveler Inbox</Text>
        <Text style={styles.sub}>Log in to manage connection requests and coordinate trips.</Text>
        <TouchableOpacity style={styles.loginBtn} onPress={() => onOpenAuth('login')}>
          <Text style={styles.loginBtnText}>Sign In</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Traveler Connections</Text>
        <Text style={styles.headerSub}>Contact details protected until mutual connection</Text>
      </View>

      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'received' && styles.tabActive]}
          onPress={() => setActiveTab('received')}
        >
          <Text style={[styles.tabText, activeTab === 'received' && styles.tabTextActive]}>
            Received ({received.length})
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'sent' && styles.tabActive]}
          onPress={() => setActiveTab('sent')}
        >
          <Text style={[styles.tabText, activeTab === 'sent' && styles.tabTextActive]}>
            Sent ({sent.length})
          </Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator color={THEME.colors.primary} size="large" />
        </View>
      ) : activeTab === 'received' ? (
        received.length === 0 ? (
          <View style={styles.centerContainer}>
            <Ionicons name="chatbubbles-outline" size={40} color={THEME.colors.textMuted} />
            <Text style={styles.emptyTitle}>No received invitations</Text>
            <Text style={styles.emptySub}>When travelers reach out to connect, they will appear here.</Text>
          </View>
        ) : (
          <FlatList
            data={received}
            keyExtractor={(item) => item.id.toString()}
            contentContainerStyle={styles.list}
            renderItem={({ item }) => (
              <View style={styles.card}>
                <View style={styles.cardHeader}>
                  <Text style={styles.name}>{item.from_user_name}</Text>
                  <View style={styles.destBadge}>
                    <Text style={styles.destBadgeText}>{item.destination}</Text>
                  </View>
                </View>

                {item.note ? <Text style={styles.note}>"{item.note}"</Text> : null}

                {item.status === 'accepted' && item.revealed_contact ? (
                  <View style={styles.contactUnlocked}>
                    <Ionicons name="checkmark-circle" size={14} color={THEME.colors.primary} />
                    <Text style={styles.contactText}>Contact: {item.revealed_contact}</Text>
                  </View>
                ) : item.status === 'pending' ? (
                  <View style={styles.actionRow}>
                    <TouchableOpacity style={styles.acceptBtn} onPress={() => handleAccept(item.id)}>
                      <Text style={styles.acceptBtnText}>Accept</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.declineBtn} onPress={() => handleDecline(item.id)}>
                      <Text style={styles.declineBtnText}>Decline</Text>
                    </TouchableOpacity>
                  </View>
                ) : (
                  <Text style={styles.statusText}>Status: {item.status}</Text>
                )}
              </View>
            )}
          />
        )
      ) : (
        sent.length === 0 ? (
          <View style={styles.centerContainer}>
            <Ionicons name="paper-plane-outline" size={40} color={THEME.colors.textMuted} />
            <Text style={styles.emptyTitle}>No sent requests</Text>
            <Text style={styles.emptySub}>Connect with compatible travelers on any destination page.</Text>
          </View>
        ) : (
          <FlatList
            data={sent}
            keyExtractor={(item) => item.id.toString()}
            contentContainerStyle={styles.list}
            renderItem={({ item }) => (
              <View style={styles.card}>
                <View style={styles.cardHeader}>
                  <Text style={styles.name}>To: {item.to_user_name}</Text>
                  <View style={[styles.destBadge, item.status === 'accepted' && { backgroundColor: 'rgba(16,185,129,0.2)' }]}>
                    <Text style={[styles.destBadgeText, item.status === 'accepted' && { color: THEME.colors.primary }]}>
                      {item.status.toUpperCase()}
                    </Text>
                  </View>
                </View>
                <Text style={styles.destSub}>Destination: {item.destination}</Text>
                {item.status === 'accepted' && item.revealed_contact ? (
                  <View style={styles.contactUnlocked}>
                    <Text style={styles.contactText}>Unlocked Contact: {item.revealed_contact}</Text>
                  </View>
                ) : null}
              </View>
            )}
          />
        )
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
  tabBar: { flexDirection: 'row', borderBottomWidth: 1, borderBottomColor: THEME.colors.border },
  tab: { flex: 1, paddingVertical: 12, alignItems: 'center' },
  tabActive: { borderBottomWidth: 2, borderBottomColor: THEME.colors.primary },
  tabText: { color: THEME.colors.textMuted, fontSize: 13, fontWeight: '600' },
  tabTextActive: { color: '#fff', fontWeight: '800' },
  title: { color: '#fff', fontSize: 18, fontWeight: '700', marginTop: 12 },
  sub: { color: THEME.colors.textSecondary, fontSize: 13, textAlign: 'center', marginTop: 6, marginBottom: 18 },
  emptyTitle: { color: '#fff', fontSize: 16, fontWeight: '700', marginTop: 10 },
  emptySub: { color: THEME.colors.textMuted, fontSize: 12, textAlign: 'center', marginTop: 4 },
  loginBtn: { backgroundColor: THEME.colors.primary, paddingHorizontal: 20, paddingVertical: 10, borderRadius: THEME.radius.sm },
  loginBtnText: { color: '#fff', fontWeight: '700', fontSize: 14 },
  list: { padding: 16 },
  card: { backgroundColor: THEME.colors.bgCard, borderRadius: THEME.radius.md, padding: 14, borderWidth: 1, borderColor: THEME.colors.border, marginBottom: 10 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  name: { color: '#fff', fontSize: 15, fontWeight: '700' },
  destBadge: { backgroundColor: 'rgba(6,182,212,0.15)', paddingHorizontal: 8, paddingVertical: 3, borderRadius: THEME.radius.full },
  destBadgeText: { color: '#22D3EE', fontSize: 11, fontWeight: '600' },
  destSub: { color: THEME.colors.textMuted, fontSize: 12, marginTop: 2 },
  note: { color: THEME.colors.textSecondary, fontSize: 12, marginVertical: 8, fontStyle: 'italic' },
  actionRow: { flexDirection: 'row', gap: 8, marginTop: 10 },
  acceptBtn: { flex: 1, backgroundColor: THEME.colors.primary, paddingVertical: 8, borderRadius: 6, alignItems: 'center' },
  acceptBtnText: { color: '#fff', fontWeight: '700', fontSize: 12 },
  declineBtn: { flex: 1, backgroundColor: 'rgba(255,255,255,0.06)', paddingVertical: 8, borderRadius: 6, alignItems: 'center' },
  declineBtnText: { color: THEME.colors.textSecondary, fontSize: 12 },
  contactUnlocked: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: 'rgba(16,185,129,0.15)', padding: 8, borderRadius: 6, marginTop: 8 },
  contactText: { color: '#fff', fontSize: 12, fontWeight: '600' },
  statusText: { color: THEME.colors.textMuted, fontSize: 11, marginTop: 6 },
});
