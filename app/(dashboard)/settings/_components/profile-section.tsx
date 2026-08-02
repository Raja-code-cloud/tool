"use client";

import * as React from "react";
import { Upload } from "lucide-react";

import { FormField } from "@/components/forms";
import { Avatar, Button, Input, Textarea } from "@/components/ui";
import { useToast } from "@/hooks/use-toast";
import { LANGUAGES, PROFILE_DEFAULTS, TIMEZONES } from "@/constants/settings";
import { SelectField } from "./select-field";
import { SettingsSection } from "./settings-section";

const BIO_MAX_LENGTH = 240;

export function ProfileSection(): React.JSX.Element {
  const { toast } = useToast();
  const [fullName, setFullName] = React.useState<string>(PROFILE_DEFAULTS.fullName);
  const [jobTitle, setJobTitle] = React.useState<string>(PROFILE_DEFAULTS.jobTitle);
  const [bio, setBio] = React.useState<string>(PROFILE_DEFAULTS.bio);
  const [timezone, setTimezone] = React.useState<string>(PROFILE_DEFAULTS.timezone);
  const [language, setLanguage] = React.useState<string>(PROFILE_DEFAULTS.language);

  const nameError = fullName.trim() === "" ? "Enter your full name." : undefined;

  function handleSubmit(event: React.FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    if (nameError) return;
    toast({ title: "Profile saved", description: "Your workspace profile has been updated." });
  }

  return (
    <form onSubmit={handleSubmit}>
      <SettingsSection
        id="profile"
        title="Profile"
        description="How you appear to other members of this workspace."
        footer={
          <>
            <Button type="reset" variant="secondary" size="compact" onClick={() => setFullName(PROFILE_DEFAULTS.fullName)}>Reset</Button>
            <Button type="submit" size="compact">Save profile</Button>
          </>
        }
      >
        <div className="flex flex-col gap-4 border-b pb-5 tablet:flex-row tablet:items-center">
          <Avatar alt={fullName || "Workspace member"} size="lg" />
          <div className="min-w-0">
            <p className="text-sm font-semibold">Profile photo</p>
            <p className="mt-1 text-sm text-muted-foreground">PNG or JPG, up to 2 MB.</p>
          </div>
          <div className="tablet:ml-auto">
            <Button type="button" variant="secondary" size="compact">
              <Upload className="size-4" aria-hidden="true" />Upload
            </Button>
          </div>
        </div>

        <div className="grid gap-5 pt-5 tablet:grid-cols-2">
          <FormField id="profile-name" label="Full name" isRequired {...(nameError ? { error: nameError } : {})}>
            <Input value={fullName} onChange={(event) => setFullName(event.target.value)} autoComplete="name" />
          </FormField>

          <FormField id="profile-email" label="Email address" description="Contact an admin to change your sign-in address.">
            <Input type="email" value={PROFILE_DEFAULTS.email} readOnly autoComplete="email" />
          </FormField>

          <FormField id="profile-title" label="Job title">
            <Input value={jobTitle} onChange={(event) => setJobTitle(event.target.value)} autoComplete="organization-title" />
          </FormField>

          <SelectField
            id="profile-timezone"
            label="Timezone"
            description="Used for scheduling and reporting."
            value={timezone}
            options={TIMEZONES}
            onValueChange={setTimezone}
          />

          <SelectField id="profile-language" label="Language" value={language} options={LANGUAGES} onValueChange={setLanguage} />

          <FormField
            id="profile-bio"
            label="Bio"
            description={`${bio.length}/${BIO_MAX_LENGTH} characters`}
            className="tablet:col-span-2"
          >
            <Textarea value={bio} maxLength={BIO_MAX_LENGTH} onChange={(event) => setBio(event.target.value)} />
          </FormField>
        </div>
      </SettingsSection>
    </form>
  );
}
