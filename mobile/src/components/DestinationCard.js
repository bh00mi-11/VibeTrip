import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { THEME } from '../theme';
import { getImageUrl } from '../api';
import { Ionicons } from '@expo/vector-icons';

export default function DestinationCard({ dest, onPress }) {
  const scores = dest.scores || {};

  return (
    <TouchableOpacity style={styles.card} activeOpacity={0.88} onPress={() => onPress(dest.name)}>
      {/* Photo with Overlay */}
      <View style={styles.imageContainer}>
        <Image
          source={{ uri: getImageUrl(dest.photo_url) }}
          style={styles.image}
          resizeMode="cover"
        />
        <View style={styles.gradientOverlay} />

        {/* Top Badges */}
        <View style={styles.topBadgesRow}>
          {dest.category ? (
            <View style={styles.categoryBadge}>
              <Text style={styles.categoryBadgeText}>{dest.category}</Text>
            </View>
          ) : <View />}

          <View style={styles.badgeRightGroup}>
            {dest.overall_match_score !== undefined && (
              <View style={styles.matchBadge}>
                <Ionicons name="sparkles" size={10} color="#FFFFFF" />
                <Text style={styles.matchBadgeText}>{Math.round(dest.overall_match_score)}% Match</Text>
              </View>
            )}
          </View>
        </View>

        {/* Title over photo */}
        <View style={styles.titleContainer}>
          <Text style={styles.destName}>{dest.name}</Text>
          {(dest.state || dest.region) && (
            <View style={styles.locationRow}>
              <Ionicons name="location-sharp" size={13} color="#BAE6FD" />
              <Text style={styles.destLocation}>
                {[dest.state, dest.region].filter(Boolean).join(', ')}
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* Body with Clean Vibe Indicators */}
      <View style={styles.body}>
        <View style={styles.vibeBars}>
          <View style={styles.vibeBarRow}>
            <Text style={styles.vibeLabel}>Nature</Text>
            <View style={styles.barTrack}>
              <View style={[styles.barFill, { width: `${scores.nature || 0}%`, backgroundColor: THEME.colors.vibeNature }]} />
            </View>
            <Text style={styles.vibeVal}>{Math.round(scores.nature || 0)}</Text>
          </View>

          <View style={styles.vibeBarRow}>
            <Text style={styles.vibeLabel}>Adventure</Text>
            <View style={styles.barTrack}>
              <View style={[styles.barFill, { width: `${scores.adventure || 0}%`, backgroundColor: THEME.colors.vibeAdventure }]} />
            </View>
            <Text style={styles.vibeVal}>{Math.round(scores.adventure || 0)}</Text>
          </View>

          <View style={styles.vibeBarRow}>
            <Text style={styles.vibeLabel}>Peace</Text>
            <View style={styles.barTrack}>
              <View style={[styles.barFill, { width: `${scores.peacefulness || 0}%`, backgroundColor: THEME.colors.vibePeacefulness }]} />
            </View>
            <Text style={styles.vibeVal}>{Math.round(scores.peacefulness || 0)}</Text>
          </View>

          <View style={styles.vibeBarRow}>
            <Text style={styles.vibeLabel}>Visual</Text>
            <View style={styles.barTrack}>
              <View style={[styles.barFill, { width: `${scores.visual_atmosphere || 0}%`, backgroundColor: THEME.colors.vibeVisual }]} />
            </View>
            <Text style={styles.vibeVal}>{Math.round(scores.visual_atmosphere || 0)}</Text>
          </View>
        </View>

        <View style={styles.footerRow}>
          <Text style={styles.actionText}>View 3-Day Plan & Local Spots</Text>
          <Ionicons name="arrow-forward" size={15} color={THEME.colors.primary} />
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: THEME.radius.lg,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 16,
    shadowColor: '#0F172A',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.07,
    shadowRadius: 10,
    elevation: 3,
  },
  imageContainer: {
    height: 190,
    width: '100%',
    position: 'relative',
    backgroundColor: '#E2E8F0',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  gradientOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(15, 23, 42, 0.4)',
  },
  topBadgesRow: {
    position: 'absolute',
    top: 12,
    left: 12,
    right: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  badgeRightGroup: {
    flexDirection: 'row',
    gap: 6,
  },
  categoryBadge: {
    backgroundColor: 'rgba(15, 23, 42, 0.75)',
    paddingHorizontal: 9,
    paddingVertical: 4,
    borderRadius: THEME.radius.full,
  },
  categoryBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  matchBadge: {
    backgroundColor: THEME.colors.primary,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: THEME.radius.full,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    shadowColor: THEME.colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 2,
  },
  matchBadgeText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '800',
  },
  titleContainer: {
    position: 'absolute',
    bottom: 12,
    left: 14,
    right: 14,
  },
  destName: {
    color: '#FFFFFF',
    fontSize: 22,
    fontWeight: '800',
    textShadowColor: 'rgba(0,0,0,0.7)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 4,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 2,
  },
  destLocation: {
    color: '#F8FAFC',
    fontSize: 12,
    fontWeight: '600',
  },
  body: {
    padding: 14,
    backgroundColor: '#FFFFFF',
  },
  vibeBars: {
    gap: 6,
    marginBottom: 12,
  },
  vibeBarRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  vibeLabel: {
    width: 65,
    color: THEME.colors.textSecondary,
    fontSize: 11,
    fontWeight: '500',
  },
  barTrack: {
    flex: 1,
    height: 5,
    backgroundColor: '#F1F5F9',
    borderRadius: THEME.radius.full,
    marginHorizontal: 8,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: THEME.radius.full,
  },
  vibeVal: {
    width: 24,
    color: THEME.colors.textMuted,
    fontSize: 11,
    fontWeight: '700',
    textAlign: 'right',
  },
  footerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
  },
  actionText: {
    color: THEME.colors.primary,
    fontSize: 12,
    fontWeight: '700',
  },
});
