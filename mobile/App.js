import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { THEME } from './src/theme';
import { getUser, logout } from './src/api';
import HomeScreen from './src/screens/HomeScreen';
import DestinationDetailScreen from './src/screens/DestinationDetailScreen';
import SavedTripsScreen from './src/screens/SavedTripsScreen';
import InboxScreen from './src/screens/InboxScreen';
import ContributeScreen from './src/screens/ContributeScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import AuthModal from './src/components/AuthModal';
import { Ionicons } from '@expo/vector-icons';

export default function App() {
  const [user, setUser] = useState(getUser());
  const [activeTab, setActiveTab] = useState('home');
  const [selectedDest, setSelectedDest] = useState(null);
  const [authModal, setAuthModal] = useState({ visible: false, tab: 'login' });

  const handleLogout = () => {
    logout();
    setUser(null);
  };

  const handleDestinationSelect = (name) => {
    setSelectedDest(name);
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.safeArea}>
        <StatusBar style="light" backgroundColor={THEME.colors.bgDark} />

        <View style={styles.content}>
          {selectedDest ? (
            <DestinationDetailScreen
              destinationName={selectedDest}
              user={user}
              onBack={() => setSelectedDest(null)}
              onOpenAuth={(tab) => setAuthModal({ visible: true, tab })}
            />
          ) : (
            <>
              {activeTab === 'home' && (
                <HomeScreen
                  user={user}
                  onSelectDestination={handleDestinationSelect}
                  onOpenAuth={(tab) => setAuthModal({ visible: true, tab })}
                />
              )}
              {activeTab === 'trips' && (
                <SavedTripsScreen
                  user={user}
                  onOpenAuth={(tab) => setAuthModal({ visible: true, tab })}
                  onSelectDestination={handleDestinationSelect}
                />
              )}
              {activeTab === 'inbox' && (
                <InboxScreen
                  user={user}
                  onOpenAuth={(tab) => setAuthModal({ visible: true, tab })}
                />
              )}
              {activeTab === 'contribute' && (
                <ContributeScreen
                  user={user}
                  onOpenAuth={(tab) => setAuthModal({ visible: true, tab })}
                />
              )}
              {activeTab === 'profile' && (
                <ProfileScreen
                  user={user}
                  onLogout={handleLogout}
                  onOpenAuth={(tab) => setAuthModal({ visible: true, tab })}
                  onUserLogin={(u) => setUser(u)}
                />
              )}
            </>
          )}
        </View>

        {/* Bottom Tab Bar (hidden when drill down into destination detail) */}
        {!selectedDest && (
          <View style={styles.tabBar}>
            <TouchableOpacity
              style={styles.tabItem}
              onPress={() => setActiveTab('home')}
            >
              <Ionicons
                name={activeTab === 'home' ? 'compass' : 'compass-outline'}
                size={22}
                color={activeTab === 'home' ? THEME.colors.primary : THEME.colors.textMuted}
              />
              <Text style={[styles.tabLabel, activeTab === 'home' && styles.tabLabelActive]}>Explore</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.tabItem}
              onPress={() => setActiveTab('trips')}
            >
              <Ionicons
                name={activeTab === 'trips' ? 'bookmark' : 'bookmark-outline'}
                size={22}
                color={activeTab === 'trips' ? THEME.colors.primary : THEME.colors.textMuted}
              />
              <Text style={[styles.tabLabel, activeTab === 'trips' && styles.tabLabelActive]}>Trips</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.tabItem}
              onPress={() => setActiveTab('inbox')}
            >
              <Ionicons
                name={activeTab === 'inbox' ? 'mail' : 'mail-outline'}
                size={22}
                color={activeTab === 'inbox' ? THEME.colors.primary : THEME.colors.textMuted}
              />
              <Text style={[styles.tabLabel, activeTab === 'inbox' && styles.tabLabelActive]}>Inbox</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.tabItem}
              onPress={() => setActiveTab('contribute')}
            >
              <Ionicons
                name={activeTab === 'contribute' ? 'add-circle' : 'add-circle-outline'}
                size={22}
                color={activeTab === 'contribute' ? THEME.colors.primary : THEME.colors.textMuted}
              />
              <Text style={[styles.tabLabel, activeTab === 'contribute' && styles.tabLabelActive]}>Submit</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.tabItem}
              onPress={() => setActiveTab('profile')}
            >
              <Ionicons
                name={activeTab === 'profile' ? 'person' : 'person-outline'}
                size={22}
                color={activeTab === 'profile' ? THEME.colors.primary : THEME.colors.textMuted}
              />
              <Text style={[styles.tabLabel, activeTab === 'profile' && styles.tabLabelActive]}>Profile</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Authentication Modal */}
        <AuthModal
          visible={authModal.visible}
          initialTab={authModal.tab}
          onClose={() => setAuthModal({ visible: false, tab: 'login' })}
          onSuccess={(u) => setUser(u)}
        />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  content: {
    flex: 1,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    paddingVertical: 8,
    paddingHorizontal: 6,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 8,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 3,
  },
  tabLabel: {
    fontSize: 10,
    fontWeight: '600',
    color: '#64748B',
  },
  tabLabelActive: {
    color: THEME.colors.primary,
    fontWeight: '800',
  },
});
