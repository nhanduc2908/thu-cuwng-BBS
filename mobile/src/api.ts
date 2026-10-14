import * as Crypto from 'expo-crypto';
import AsyncStorage from '@react-native-async-storage/async-storage';

import {
  clearSession,
  readCache,
  saveSession,
  writeCache,
} from './storage';
import type {
  PetCareSession,
  PetCareUser,
  RpcRequestStatus,
} from './types';

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class PetCareApi {
  private session: PetCareSession;
  private refreshing: Promise<void> | null = null;

  private constructor(
    readonly baseUrl: string,
    session: PetCareSession,
  ) {
    this.session = session;
  }

  static async signIn(
    baseUrl: string,
    username: string,
    password: string,
  ): Promise<PetCareApi> {
    const normalizedUrl = validateApiUrl(baseUrl);
    const response = await fetch(`${normalizedUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.trim(), password }),
    });
    const payload = await parseResponse(response);
    const session = payload as PetCareSession;
    if (
      typeof session.access_token !== 'string' ||
      typeof session.refresh_token !== 'string' ||
      !Number.isInteger(session.user?.id) ||
      !Array.isArray(session.permissions)
    ) {
      throw new ApiError('The API returned an incomplete sign-in response.');
    }
    await saveSession(session);
    return new PetCareApi(normalizedUrl, session);
  }

  static async resume(
    baseUrl: string,
    session: PetCareSession,
  ): Promise<PetCareApi> {
    if (
      typeof session.access_token !== 'string' ||
      !session.access_token ||
      typeof session.refresh_token !== 'string' ||
      !session.refresh_token ||
      !Number.isInteger(session.user?.id) ||
      !Array.isArray(session.permissions)
    ) {
      throw new ApiError('The saved session is incomplete. Please sign in again.');
    }
    return new PetCareApi(validateApiUrl(baseUrl), session);
  }

  get user(): PetCareUser {
    return this.session.user;
  }

  get permissions(): ReadonlySet<string> {
    return new Set(this.session.permissions);
  }

  can(permission: string): boolean {
    return this.session.permissions.includes(permission);
  }

  async signOut(): Promise<void> {
    this.session = {
      ...this.session,
      access_token: '',
      refresh_token: '',
      permissions: [],
    };
    await clearSession();
  }

  async read<T>(
    method: string,
    args: unknown[] = [],
    cacheKey = JSON.stringify([method, args]),
  ): Promise<{ data: T; fromCache: boolean }> {
    try {
      const data = await this.rpc<T>(method, args);
      await writeCache(this.user.id, cacheKey, data);
      return { data, fromCache: false };
    } catch (error) {
      const cached = await readCache<T>(this.user.id, cacheKey);
      if (cached !== null && isNetworkError(error)) {
        return { data: cached, fromCache: true };
      }
      throw error;
    }
  }

  async rpc<T>(
    method: string,
    args: unknown[] = [],
    requestId?: string,
  ): Promise<T> {
    const body: Record<string, unknown> = { method, args };
    if (requestId) {
      body.request_id = requestId;
    }
    const payload = await this.authenticatedRequest('/api/rpc', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return payload.result as T;
  }

  async getRequestStatus(requestId: string): Promise<RpcRequestStatus> {
    return (await this.authenticatedRequest(
      `/api/rpc/requests/${encodeURIComponent(requestId)}`,
    )) as RpcRequestStatus;
  }

  async refreshProfile(): Promise<void> {
    const payload = await this.authenticatedRequest('/api/auth/me');
    if (!payload.user || !Array.isArray(payload.permissions)) {
      throw new ApiError('The API returned an incomplete profile response.');
    }
    this.session = {
      ...this.session,
      user: payload.user as PetCareUser,
      permissions: payload.permissions as string[],
    };
    await saveSession(this.session);
  }

  async changePassword(
    currentPassword: string,
    newPassword: string,
  ): Promise<void> {
    await this.authenticatedRequest('/api/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
    this.session = {
      ...this.session,
      user: { ...this.session.user, must_change_password: false },
    };
    await saveSession(this.session);
  }

  async forgetCachedData(): Promise<void> {
    const keys = await AsyncStorage.getAllKeys();
    const scopedPrefix = `petcare.mobile.cache.v1.${this.user.id}.`;
    const matching = keys.filter((key) => key.startsWith(scopedPrefix));
    if (matching.length > 0) {
      await AsyncStorage.multiRemove(matching);
    }
  }

  private async authenticatedRequest(
    path: string,
    init: RequestInit = {},
  ): Promise<Record<string, any>> {
    let response = await this.send(path, init);
    if (response.status === 401 && this.session.refresh_token) {
      await this.refreshTokens();
      response = await this.send(path, init);
    }
    if (response.status === 401) {
      await this.signOut();
      throw new ApiError('Your session expired. Please sign in again.', 401);
    }
    return parseResponse(response);
  }

  private async send(path: string, init: RequestInit): Promise<Response> {
    try {
      return await fetch(`${this.baseUrl}${path}`, {
        ...init,
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.session.access_token}`,
          ...init.headers,
        },
      });
    } catch (error) {
      throw new ApiError(
        error instanceof Error
          ? `Could not reach the PetCare service: ${error.message}`
          : 'Could not reach the PetCare service.',
      );
    }
  }

  private async refreshTokens(): Promise<void> {
    if (this.refreshing) {
      await this.refreshing;
      return;
    }
    this.refreshing = (async () => {
      let response: Response;
      try {
        response = await fetch(`${this.baseUrl}/api/auth/refresh`, {
          method: 'POST',
          headers: {
            Accept: 'application/json',
            Authorization: `Bearer ${this.session.refresh_token}`,
          },
        });
      } catch (error) {
        throw new ApiError(
          error instanceof Error
            ? `Could not refresh the PetCare session: ${error.message}`
            : 'Could not refresh the PetCare session.',
        );
      }
      let payload: Record<string, any>;
      try {
        payload = await parseResponse(response);
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          await this.signOut();
          throw new ApiError('Your session expired. Please sign in again.', 401);
        }
        throw error;
      }
      this.session = {
        ...this.session,
        access_token: requireToken(payload.access_token, 'access'),
        refresh_token: requireToken(payload.refresh_token, 'refresh'),
        user: (payload.user as PetCareUser) ?? this.session.user,
        permissions: Array.isArray(payload.permissions)
          ? (payload.permissions as string[])
          : this.session.permissions,
      };
      await saveSession(this.session);
    })();
    try {
      await this.refreshing;
    } finally {
      this.refreshing = null;
    }
  }
}

export function createRequestId(): string {
  return Crypto.randomUUID();
}

export function validateApiUrl(value: string): string {
  const url = value.trim().replace(/\/+$/, '');
  let parsed: URL;
  try {
    parsed = new URL(url);
  } catch {
    throw new ApiError('Enter a valid API address, including https://.');
  }
  if (parsed.protocol !== 'https:' || !parsed.hostname) {
    throw new ApiError('For mobile devices, the central API address must use HTTPS.');
  }
  if (parsed.username || parsed.password || parsed.search || parsed.hash) {
    throw new ApiError('The API address cannot contain credentials or URL parameters.');
  }
  return url;
}

async function parseResponse(response: Response): Promise<any> {
  let payload: any;
  try {
    payload = await response.json();
  } catch {
    throw new ApiError(
      `The API returned an invalid response (HTTP ${response.status}).`,
      response.status,
    );
  }
  if (!response.ok) {
    const message =
      typeof payload?.detail === 'string'
        ? payload.detail
        : `The API request failed (HTTP ${response.status}).`;
    throw new ApiError(message, response.status);
  }
  return payload;
}

function isNetworkError(error: unknown): boolean {
  return error instanceof ApiError && error.status === undefined;
}

function requireToken(value: unknown, tokenType: string): string {
  if (typeof value !== 'string' || value.length === 0) {
    throw new ApiError(`The API returned an invalid ${tokenType} token.`);
  }
  return value;
}
