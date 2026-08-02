"use client";

import { Upload } from "lucide-react";
import * as React from "react";

import { FormField } from "@/components/forms";
import { Avatar, Button, Input, Textarea } from "@/components/ui";
import { LANGUAGES, TIMEZONES } from "@/constants/settings";
import { useToast } from "@/hooks/use-toast";

import { SelectField } from "./select-field";
import { SettingsSection } from "./settings-section";
import { useSettingsState } from "./use-settings-state";

const BIO_MAX_LENGTH = 240;

export function ProfileSection(): React.JSX.Element {
  const { toast } = useToast();
  const { profile, isLoading, isSaving, error, saveProfile, uploadAvatar, reload } =
    useSettingsState();
  const [fullName, setFullName] = React.useState("");
  const [jobTitle, setJobTitle] = React.useState("");
  const [bio, setBio] = React.useState("");
  const [timezone, setTimezone] = React.useState("");
  const [language, setLanguage] = React.useState("");
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    if (!profile) return;
    setFullName(profile.fullName);
    setJobTitle(profile.jobTitle);
    setBio(profile.bio);
    setTimezone(profile.timezone);
    setLanguage(profile.language);
  }, [profile]);

  const nameError = fullName.trim() === "" ? "Enter your full name." : undefined;

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (nameError) return;
    const saved = await saveProfile({ fullName, timezone, language });
    if (saved) {
      toast({ title: "Profile saved", description: "Your workspace profile has been updated." });
    } else if (error) {
      toast({ title: "Could not save profile", description: error });
    }
  }

  async function handleAvatarChange(event: React.ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    if (!file) return;
    const uploaded = await uploadAvatar(file);
    if (uploaded) {
      toast({ title: "Avatar updated", description: "Your profile photo has been uploaded." });
    } else if (error) {
      toast({ title: "Upload failed", description: error });
    }
    event.target.value = "";
  }

  if (isLoading && !profile) {
    return (
      <SettingsSection id="profile" title="Profile" description="Loading profile…">
        <p className="text-muted-foreground text-sm">Loading profile…</p>
      </SettingsSection>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <SettingsSection
        id="profile"
        title="Profile"
        description="How you appear to other members of this workspace."
        footer={
          <>
            <Button
              type="button"
              variant="secondary"
              size="compact"
              disabled={isSaving}
              onClick={() => void reload()}
            >
              Reload
            </Button>
            <Button type="submit" size="compact" disabled={isSaving || Boolean(nameError)}>
              {isSaving ? "Saving…" : "Save profile"}
            </Button>
          </>
        }
      >
        <div className="tablet:flex-row tablet:items-center flex flex-col gap-4 border-b pb-5">
          <Avatar
            alt={fullName || "Workspace member"}
            size="lg"
            {...(profile?.avatarUrl ? { src: profile.avatarUrl } : {})}
          />
          <div className="min-w-0">
            <p className="text-sm font-semibold">Profile photo</p>
            <p className="text-muted-foreground mt-1 text-sm">PNG or JPG, up to 2 MB.</p>
          </div>
          <div className="tablet:ml-auto">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              className="sr-only"
              onChange={handleAvatarChange}
            />
            <Button
              type="button"
              variant="secondary"
              size="compact"
              disabled={isSaving}
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="size-4" aria-hidden="true" />
              Upload
            </Button>
          </div>
        </div>

        <div className="tablet:grid-cols-2 grid gap-5 pt-5">
          <FormField
            id="profile-name"
            label="Full name"
            isRequired
            {...(nameError ? { error: nameError } : {})}
          >
            <Input
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              autoComplete="name"
            />
          </FormField>

          <FormField
            id="profile-email"
            label="Email address"
            description="Contact an admin to change your sign-in address."
          >
            <Input type="email" value={profile?.email ?? ""} readOnly autoComplete="email" />
          </FormField>

          <FormField id="profile-title" label="Job title">
            <Input
              value={jobTitle}
              onChange={(event) => setJobTitle(event.target.value)}
              autoComplete="organization-title"
            />
          </FormField>

          <SelectField
            id="profile-timezone"
            label="Timezone"
            description="Used for scheduling and reporting."
            value={timezone}
            options={TIMEZONES}
            onValueChange={setTimezone}
          />

          <SelectField
            id="profile-language"
            label="Language"
            value={language}
            options={LANGUAGES}
            onValueChange={setLanguage}
          />

          <FormField
            id="profile-bio"
            label="Bio"
            description={`${bio.length}/${BIO_MAX_LENGTH} characters`}
            className="tablet:col-span-2"
          >
            <Textarea
              value={bio}
              maxLength={BIO_MAX_LENGTH}
              onChange={(event) => setBio(event.target.value)}
            />
          </FormField>
        </div>
      </SettingsSection>
    </form>
  );
}
