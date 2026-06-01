import { ObjectType } from '@/types';

export interface ObjectDefinition {
  type: ObjectType;
  label: string;
  emoji: string;
  category: 'shapes' | 'nature' | 'buildings' | 'animals' | 'characters' | 'props';
  defaultColor: string;
}

export const OBJECT_CATALOG: ObjectDefinition[] = [
  { type: 'cube', label: 'Box', emoji: '📦', category: 'shapes', defaultColor: '#4FC3F7' },
  { type: 'sphere', label: 'Ball', emoji: '⚽', category: 'shapes', defaultColor: '#FF7043' },
  { type: 'cylinder', label: 'Tube', emoji: '🧱', category: 'shapes', defaultColor: '#AB47BC' },
  { type: 'cone', label: 'Cone', emoji: '🔺', category: 'shapes', defaultColor: '#FFA726' },
  { type: 'tree', label: 'Tree', emoji: '🌲', category: 'nature', defaultColor: '#66BB6A' },
  { type: 'flower', label: 'Flower', emoji: '🌸', category: 'nature', defaultColor: '#EC407A' },
  { type: 'rock', label: 'Rock', emoji: '🪨', category: 'nature', defaultColor: '#78909C' },
  { type: 'mushroom', label: 'Mushroom', emoji: '🍄', category: 'nature', defaultColor: '#EF5350' },
  { type: 'cloud', label: 'Cloud', emoji: '☁️', category: 'nature', defaultColor: '#ECEFF1' },
  { type: 'star', label: 'Star', emoji: '⭐', category: 'nature', defaultColor: '#FFEE58' },
  { type: 'house', label: 'House', emoji: '🏠', category: 'buildings', defaultColor: '#8D6E63' },
  { type: 'fence', label: 'Fence', emoji: '🏗️', category: 'buildings', defaultColor: '#A1887F' },
  { type: 'bridge', label: 'Bridge', emoji: '🌉', category: 'buildings', defaultColor: '#BCAAA4' },
  { type: 'lamp', label: 'Lamp', emoji: '💡', category: 'buildings', defaultColor: '#FFF176' },
  { type: 'animal_cat', label: 'Cat', emoji: '🐱', category: 'animals', defaultColor: '#FFB74D' },
  { type: 'animal_dog', label: 'Dog', emoji: '🐶', category: 'animals', defaultColor: '#8D6E63' },
  { type: 'animal_bird', label: 'Bird', emoji: '🐦', category: 'animals', defaultColor: '#42A5F5' },
  { type: 'animal_fish', label: 'Fish', emoji: '🐟', category: 'animals', defaultColor: '#26C6DA' },
  { type: 'character_kid', label: 'Kid', emoji: '🧒', category: 'characters', defaultColor: '#FFB74D' },
  { type: 'character_robot', label: 'Robot', emoji: '🤖', category: 'characters', defaultColor: '#90A4AE' },
];

export const CATEGORIES = [
  { id: 'shapes' as const, label: 'Shapes', emoji: '🔷' },
  { id: 'nature' as const, label: 'Nature', emoji: '🌿' },
  { id: 'buildings' as const, label: 'Build', emoji: '🏗️' },
  { id: 'animals' as const, label: 'Animals', emoji: '🐾' },
  { id: 'characters' as const, label: 'People', emoji: '👤' },
  { id: 'props' as const, label: 'Props', emoji: '✨' },
];

export const ENVIRONMENT_THEMES = [
  { id: 'meadow' as const, label: 'Sunny Meadow', emoji: '🌻', groundColor: '#7CB342', skyColor: '#87CEEB', fogColor: '#E8F5E9' },
  { id: 'night' as const, label: 'Starry Night', emoji: '🌙', groundColor: '#1B5E20', skyColor: '#0D1B2A', fogColor: '#1B2838' },
  { id: 'underwater' as const, label: 'Underwater', emoji: '🐠', groundColor: '#00695C', skyColor: '#006064', fogColor: '#004D40' },
  { id: 'space' as const, label: 'Outer Space', emoji: '🚀', groundColor: '#37474F', skyColor: '#000000', fogColor: '#1A1A2E' },
  { id: 'desert' as const, label: 'Desert', emoji: '🏜️', groundColor: '#E6A23C', skyColor: '#FFB74D', fogColor: '#FFF3E0' },
  { id: 'snow' as const, label: 'Snow Land', emoji: '❄️', groundColor: '#E0E0E0', skyColor: '#B3E5FC', fogColor: '#E1F5FE' },
  { id: 'sunset' as const, label: 'Sunset', emoji: '🌅', groundColor: '#5D4037', skyColor: '#FF7043', fogColor: '#FBE9E7' },
  { id: 'candy' as const, label: 'Candy World', emoji: '🍭', groundColor: '#F48FB1', skyColor: '#CE93D8', fogColor: '#FCE4EC' },
];

export const COLORS = [
  '#EF5350', '#EC407A', '#AB47BC', '#7E57C2',
  '#5C6BC0', '#42A5F5', '#29B6F6', '#26C6DA',
  '#26A69A', '#66BB6A', '#9CCC65', '#D4E157',
  '#FFEE58', '#FFA726', '#FF7043', '#8D6E63',
  '#BDBDBD', '#78909C', '#FFFFFF', '#263238',
];

export const AVATARS = [
  '🦊', '🐰', '🐻', '🐼', '🐸',
  '🦉', '🦋', '🐙', '🦄', '🐲',
  '🌟', '🌈',
];
