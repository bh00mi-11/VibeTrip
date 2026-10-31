import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl, ActivityIndicator, TouchableOpacity } from 'react-native';
import { THEME } from '../theme';
import VibeSelector from '../components/VibeSelector';
import DestinationCard from '../components/DestinationCard';
import { recommendDestinations, searchDestinationsByImage } from '../api';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';

export default function HomeScreen({ user, onSelectDestination, onOpenAuth }) {
  const [vibes, setVibes] = useState({
    nature: 'high',
    adventure: 'medium',
    peacefulness: 'high',
    crowd_match: 'medium',
    visual_atmosphere: 'high',
  });
  const [query, setQuery] = useState('');
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [activePhoto, setActivePhoto] = useState(null);

  useEffect(() => {
    loadDestinations(vibes, query);
  }, []);

  const loadDestinations = async (targetVibes, q = query) => {
    try {
      setLoading(true);
      const res = await recommendDestinations(targetVibes, q);
      setDestinations(res.recommendations || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handlePickImage = async () => {
    try {
      const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!permission.granted) {
        alert('Permission to access photo gallery is required for visual vibe search.');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets[0]) {
        const asset = result.assets[0];
        setActivePhoto(asset);
        setLoading(true);

        const formData = new FormData();
        const filename = asset.uri.split('/').pop() || 'photo.jpg';
        const match = /\.(\w+)$/.exec(filename);
        const type = match ? `image/${match[1]}` : `image/jpeg`;

        formData.append('photo', {
          uri: asset.uri,
          name: filename,
          type: type,
        });
        if (query) {
          formData.append('query_text', query);
        }

        const res = await searchDestinationsByImage(formData);
        if (res.recommendations) {
          setDestinations(res.recommendations);
        }
        if (res.recommended_sliders) {
          setVibes(res.recommended_sliders);
        }
      }
    } catch (err) {
      console.error('Visual vibe search error:', err);
      alert('Photo search failed: ' + (err.message || 'Please check backend connection.'));
    } finally {
      setLoading(false);
    }
  };

  const handleClearPhoto = () => {
    setActivePhoto(null);
    loadDestinations(vibes, query);
  };

  const handleVibeChange = (newVibes) => {
    setVibes(newVibes);
    loadDestinations(newVibes, query);
  };

  const handleSearch = () => {
    loadDestinations(vibes, query);
  };

  const handleRefresh = () => {
    setRefreshing(true);
    if (activePhoto) {
      handlePickImage();
    } else {
      loadDestinations(vibes, query);
    }
  };

  return (
    <View style={styles.container}>
      {/* Header bar */}
      <View style={styles.header}>
        <View style={styles.brandRow}>
          <View style={styles.logoBadge}>
            <Ionicons name="compass" size={20} color="#fff" />
          </View>
          <View>
            <Text style={styles.brandTitle}>VibeTrip</Text>
            <Text style={styles.brandSub}>AI Multi-Modal Travel</Text>
          </View>
        </View>

        {!user && (
          <TouchableOpacity style={styles.authBtn} onPress={() => onOpenAuth('login')}>
            <Text style={styles.authBtnText}>Sign In</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Main List */}
      <FlatList
        data={destinations}
        keyExtractor={(item) => item.name}
        renderItem={({ item }) => (
          <DestinationCard dest={item} onPress={onSelectDestination} />
        )}
        ListHeaderComponent={
          <>
            <VibeSelector
              vibes={vibes}
              onChange={handleVibeChange}
              query={query}
              onQueryChange={setQuery}
              onSearch={handleSearch}
              loading={loading}
              activePhoto={activePhoto}
              onPickImage={handlePickImage}
              onClearPhoto={handleClearPhoto}
            />
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Curated Destinations</Text>
              <Text style={styles.sectionSubtitle}>
                {destinations.length} matches found
              </Text>
            </View>
          </>
        }
        ListEmptyComponent={
          loading ? (
            <View style={styles.centerBox}>
              <ActivityIndicator color={THEME.colors.primary} size="large" />
              <Text style={styles.emptyText}>Matching AI visual & text embeddings...</Text>
            </View>
          ) : (
            <View style={styles.centerBox}>
              <Text style={styles.emptyText}>No destinations matched your vibes.</Text>
            </View>
          )
        }
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={THEME.colors.primary}
          />
        }
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  logoBadge: {
    width: 34,
    height: 34,
    borderRadius: THEME.radius.sm,
    backgroundColor: THEME.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  brandTitle: {
    color: '#0F172A',
    fontSize: 18,
    fontWeight: '800',
  },
  brandSub: {
    color: THEME.colors.textSecondary,
    fontSize: 10,
  },
  authBtn: {
    backgroundColor: '#E0F2FE',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: THEME.radius.sm,
    borderWidth: 1,
    borderColor: '#BAE6FD',
  },
  authBtnText: {
    color: THEME.colors.primary,
    fontSize: 12,
    fontWeight: '700',
  },
  listContent: {
    padding: 16,
    paddingBottom: 80,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    marginTop: 4,
  },
  sectionTitle: {
    color: '#0F172A',
    fontSize: 16,
    fontWeight: '800',
  },
  sectionSubtitle: {
    color: THEME.colors.textSecondary,
    fontSize: 12,
  },
  centerBox: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    color: THEME.colors.textSecondary,
    fontSize: 13,
    marginTop: 10,
  },
});
