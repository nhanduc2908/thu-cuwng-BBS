import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

import type { PetCareSession, RpcDraft } from './types';

const SESSION_KEY = 'petcare.mobile.session.v1';
const API_URL_KEY = 'petcare.mobile.api-url.v1';
const CACHE_PREFIX = 'petcare.mobile.cache.v1';
const DRAFTS_PREFIX = 'petcare.mobile.drafts.v1';

export async function getSavedApiUrl(): Promise<string> {
  return (await AsyncStorage.getItem(API_URL_KEY)) ?? '';
}

export async function saveApiUrl(value: string): Promise<void> {
  await AsyncStorage.setItem(API_URL_KEY, value.trim());
}

export async function loadSession(): Promise<PetCareSession | null> {
  const value = await SecureStore.getItemAsync(SESSION_KEY);
  if (!value) {
    return null;
  }
  try {
    const parsed: unknown = JSON.parse(value);
    if (!isSession(parsed)) {
      await clearSession();
      return null;
    }
    return parsed;
  } catch {
    await clearSession();
    return null;
  }
}

export async function saveSession(session: PetCareSession): Promise<void> {
  await SecureStore.setItemAsync(SESSION_KEY, JSON.stringify(session));
}

export async function clearSession(): Promise<void> {
  await SecureStore.deleteItemAsync(SESSION_KEY);
}

function scopedKey(prefix: string, userId: number, key: string): string {
  return `${prefix}.${userId}.${encodeURIComponent(key)}`;
}

export async function readCache<T>(
  userId: number,
  key: string,
): Promise<T | null> {
  const value = await AsyncStorage.getItem(scopedKey(CACHE_PREFIX, userId, key));
  if (!value) {
    return null;
  }
  try {
    return JSON.parse(value) as T;
  } catch {
    return null;
  }
}

export async function writeCache(
  userId: number,
  key: string,
  value: unknown,
): Promise<void> {
  await AsyncStorage.setItem(
    scopedKey(CACHE_PREFIX, userId, key),
    JSON.stringify(value),
  );
}

export async function readDrafts(userId: number): Promise<RpcDraft[]> {
  const value = await AsyncStorage.getItem(
    scopedKey(DRAFTS_PREFIX, userId, 'outbox'),
  );
  if (!value) {
    return [];
  }
  try {
    const parsed: unknown = JSON.parse(value);
    if (
      !Array.isArray(parsed) ||
      !parsed.every(isDraftForUser.bind(null, userId))
    ) {
      throw new Error('The saved offline request queue is invalid.');
    }
    return parsed;
  } catch {
    throw new Error('Could not read the saved offline request queue.');
  }
}

export async function writeDrafts(
  userId: number,
  drafts: RpcDraft[],
): Promise<void> {
  await AsyncStorage.setItem(
    scopedKey(DRAFTS_PREFIX, userId, 'outbox'),
    JSON.stringify(drafts),
  );
}

function isSession(value: unknown): value is PetCareSession {
  if (!isRecord(value) || !isRecord(value.user)) return false;
  return (
    typeof value.access_token === 'string' &&
    value.access_token.length > 0 &&
    typeof value.refresh_token === 'string' &&
    value.refresh_token.length > 0 &&
    Number.isInteger(value.user.id) &&
    Array.isArray(value.permissions) &&
    value.permissions.every((permission) => typeof permission === 'string')
  );
}

function isDraftForUser(userId: number, value: unknown): value is RpcDraft {
  return (
    isRecord(value) &&
    value.userId === userId &&
    typeof value.requestId === 'string' &&
    typeof value.title === 'string' &&
    typeof value.method === 'string' &&
    Array.isArray(value.args) &&
    typeof value.createdAt === 'string' &&
    (value.status === 'queued' || value.status === 'needs-review')
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}
