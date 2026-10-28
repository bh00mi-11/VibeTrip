import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, ScrollView, ActivityIndicator } from 'react-native';
import { THEME } from '../theme';
import { Ionicons } from '@expo/vector-icons';

const DIMS = [
  { key: 'nature', label: 'Nature', icon: 'leaf-outline', color: THEME.colors.vibeNature },
  { key: 'adventure', label: 'Adventure', icon: 'bicycle-outline', color: THEME.colors.vibeAdventure },
  { key: 'peacefulness', label: 'Peacefulness', icon: 'water-outline', color: THEME.colors.vibePeacefulness },
  { key: 'crowd_match', label: 'Crowd Vibe', icon: 'people-outline', color: THEME.colors.vibeCrowd },
  { key: 'visual_atmosphere', label: 'Visual', icon: 'sparkles-outline', color: THEME.colors.vibeVisual },
];

const PRESETS = [
  { name: '🌿 Nature Retreat', vibes: { nature: 'high', adventure: 'low', peacefulness: 'high', crowd_match: 'low', visual_atmosphere: 'high' } },
  { name: '🧗 High Adventure', vibes: { nature: 'high', adventure: 'high', peacefulness: 'low', crowd_match: 'high', visual_atmosphere: 'high' } },
  { name: '🎉 Vibrant & Lively', vibes: { nature: 'medium', adventure: 'medium', peacefulness: 'low', crowd_match: 'high', visual_atmosphere: 'high' } },
  { name: '🧘 Calm Solitude', vibes: { nature: 'high', adventure: 'medium', peacefulness: 'high', crowd_match: 'low', visual_atmosphere: 'high' } },
];

export default function VibeSelector({ vibes, onChange, query, onQueryChange, onSearch, loading }) {
  const setLevel = (dim, level) => {
    onChange({ ...vibes, [dim]: level });
  };

  return (
    <View style={styles.container}>
      {/* Title / Description */}
      <View style={styles.titleRow}>
        <Ionicons name="options-outline" size={18} color={THEME.colors.primary} />
        <Text style={styles.cardTitle}>Find Destinations by Vibe & Search</Text>
      </View>

      {/* Prominent Search Bar with Clear & Search Button */}
      <View style={styles.searchRow}>
        <Ionicons name="search" size={18} color={THEME.colors.primary} style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search place name, activity (e.g. Goa, rafting)..."
          placeholderTextColor={THEME.colors.textMuted}
          value={query}
          onChangeText={onQueryChange}
          onSubmitEditing={onSearch}
          returnKeyType="search"
        />
        {query.length > 0 && (
          <TouchableOpacity onPress={() => { onQueryChange(''); onSearch(); }} style={styles.clearBtn}>
            <Ionicons name="close-circle" size={16} color={THEME.colors.textMuted} />
          </TouchableOpacity>
        )}
      </View>

      {/* Preset Chips */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.presetScroll}>
        {PRESETS.map((p) => (
          <TouchableOpacity
            key={p.name}
            style={styles.presetChip}
            onPress={() => onChange(p.vibes)}
          >
            <Text style={styles.presetChipText}>{p.name}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Vibe Dimension Filters */}
      <View style={styles.dimsGrid}>
        {DIMS.map((d) => {
          const current = vibes[d.key] || 'medium';
          return (
            <View key={d.key} style={styles.dimRow}>
              <View style={styles.dimLabelGroup}>
                <Ionicons name={d.icon} size={15} color={d.color} />
                <Text style={styles.dimLabel}>{d.label}</Text>
              </View>

              <View style={styles.levelGroup}>
                {['low', 'medium', 'high'].map((lvl) => (
                  <TouchableOpacity
                    key={lvl}
                    style={[
                      styles.levelBtn,
                      current === lvl && { backgroundColor: d.color, borderColor: d.color }
                    ]}
                    onPress={() => setLevel(d.key, lvl)}
                  >
                    <Text style={[
                      styles.levelBtnText,
                      current === lvl && styles.levelBtnTextActive
                    ]}>
                      {lvl.charAt(0).toUpperCase() + lvl.slice(1, 3)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          );
        })}
      </View>

      {/* Big Action Search / Apply Button */}
      <TouchableOpacity
        style={styles.actionSearchBtn}
        onPress={onSearch}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#FFFFFF" size="small" />
        ) : (
          <View style={styles.btnContent}>
            <Ionicons name="sparkles" size={16} color="#FFFFFF" />
            <Text style={styles.actionSearchBtnText}>Search & Match Destinations</Text>
          </View>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: THEME.radius.lg,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 16,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: 10,
    elevation: 3,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: THEME.colors.textMain,
  },
  searchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderRadius: THEME.radius.md,
    paddingHorizontal: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    height: 44,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    height: 44,
    color: THEME.colors.textMain,
    fontSize: 13,
  },
  clearBtn: {
    padding: 4,
  },
  presetScroll: {
    marginBottom: 14,
  },
  presetChip: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: THEME.radius.full,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  presetChipText: {
    color: THEME.colors.textSecondary,
    fontSize: 12,
    fontWeight: '600',
  },
  dimsGrid: {
    gap: 10,
    marginBottom: 14,
  },
  dimRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  dimLabelGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    width: 110,
  },
  dimLabel: {
    color: THEME.colors.textMain,
    fontSize: 13,
    fontWeight: '600',
  },
  levelGroup: {
    flexDirection: 'row',
    backgroundColor: '#F1F5F9',
    borderRadius: THEME.radius.sm,
    padding: 2,
    flex: 1,
    justifyContent: 'flex-end',
    maxWidth: 180,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  levelBtn: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: 6,
  },
  levelBtnText: {
    color: THEME.colors.textSecondary,
    fontSize: 11,
    fontWeight: '600',
  },
  levelBtnTextActive: {
    color: '#FFFFFF',
    fontWeight: '800',
  },
  actionSearchBtn: {
    backgroundColor: THEME.colors.primary,
    borderRadius: THEME.radius.md,
    paddingVertical: 12,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: THEME.colors.primary,
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.25,
    shadowRadius: 6,
    elevation: 3,
  },
  btnContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  actionSearchBtnText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 14,
  },
});
