"use client";

import * as React from "react";

import { getApiErrorMessage, isApiError } from "@/lib/api/errors";
import type { NotificationChannelId } from "@/lib/domain/settings";
import { isBackendSettingsEnabled, settingsService } from "@/lib/services";
import type { ProfileState } from "@/lib/settings/mappers";

type ChannelState = Record<NotificationChannelId, { email: boolean; inApp: boolean }>;

export function useSettingsState() {
  const [profile, setProfile] = React.useState<ProfileState | null>(null);
  const [notificationPreferences, setNotificationPreferences] = React.useState<ChannelState | null>(
    null,
  );
  const [isLoading, setIsLoading] = React.useState(true);
  const [isSaving, setIsSaving] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const load = React.useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [loadedProfile, preferences] = await Promise.all([
        settingsService.getProfile(),
        settingsService.listNotificationPreferences(),
      ]);
      setProfile(loadedProfile);
      setNotificationPreferences(
        preferences.reduce<ChannelState>((accumulator, preference) => {
          accumulator[preference.id] = { email: preference.email, inApp: preference.inApp };
          return accumulator;
        }, {} as ChannelState),
      );
    } catch (loadError) {
      setError(getApiErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    void load();
  }, [load]);

  const saveProfile = React.useCallback(
    async (input: { fullName: string; timezone: string; language: string }) => {
      if (!profile) return false;
      setIsSaving(true);
      setError(null);
      try {
        const updated = await settingsService.updateProfile(
          {
            displayName: input.fullName,
            timeZone: input.timezone,
            locale: input.language,
          },
          profile.version,
        );
        setProfile(updated);
        return true;
      } catch (saveError) {
        setError(getApiErrorMessage(saveError));
        if (isApiError(saveError) && saveError.code === "unauthorized") {
          return false;
        }
        return false;
      } finally {
        setIsSaving(false);
      }
    },
    [profile],
  );

  const uploadAvatar = React.useCallback(
    async (file: File) => {
      if (!profile) return false;
      setIsSaving(true);
      setError(null);
      try {
        const updated = await settingsService.uploadAvatar(file, profile.version);
        setProfile(updated);
        return true;
      } catch (uploadError) {
        setError(getApiErrorMessage(uploadError));
        return false;
      } finally {
        setIsSaving(false);
      }
    },
    [profile],
  );

  const saveNotificationPreferences = React.useCallback(async () => {
    if (!notificationPreferences) return false;
    setIsSaving(true);
    setError(null);
    try {
      const updated = await settingsService.updateNotificationPreferences(notificationPreferences);
      setNotificationPreferences(
        updated.reduce<ChannelState>((accumulator, preference) => {
          accumulator[preference.id] = { email: preference.email, inApp: preference.inApp };
          return accumulator;
        }, {} as ChannelState),
      );
      return true;
    } catch (saveError) {
      setError(getApiErrorMessage(saveError));
      return false;
    } finally {
      setIsSaving(false);
    }
  }, [notificationPreferences]);

  const setPreference = React.useCallback(
    (id: NotificationChannelId, channel: "email" | "inApp", checked: boolean) => {
      setNotificationPreferences((current) =>
        current ? { ...current, [id]: { ...current[id], [channel]: checked } } : current,
      );
    },
    [],
  );

  return {
    profile,
    notificationPreferences,
    isLoading,
    isSaving,
    error,
    isBackendEnabled: isBackendSettingsEnabled,
    reload: load,
    saveProfile,
    uploadAvatar,
    saveNotificationPreferences,
    setPreference,
  };
}
