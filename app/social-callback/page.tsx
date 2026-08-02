"use client";

import { useRouter, useSearchParams } from "next/navigation";
import * as React from "react";

import { ROUTES } from "@/constants/navigation";
import { useToast } from "@/hooks/use-toast";
import { socialAccountService } from "@/lib/services";
import { resolveSocialAccountErrorMessage } from "@/lib/social-accounts/error-messages";
import {
  SOCIAL_OAUTH_PLATFORM_KEY,
  SOCIAL_OAUTH_RETURN_TO_KEY,
  SOCIAL_OAUTH_STATE_KEY,
  SOCIAL_OAUTH_VERIFIER_KEY,
} from "@/lib/social-accounts/oauth-storage";

function SocialCallbackHandler(): React.JSX.Element {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const [status, setStatus] = React.useState("Completing account connection…");

  React.useEffect(() => {
    async function completeSocialOAuth(): Promise<void> {
      const code = searchParams.get("code");
      const state = searchParams.get("state");
      const error = searchParams.get("error");
      const storedState = sessionStorage.getItem(SOCIAL_OAUTH_STATE_KEY);
      const codeVerifier = sessionStorage.getItem(SOCIAL_OAUTH_VERIFIER_KEY);
      const platformCode = sessionStorage.getItem(SOCIAL_OAUTH_PLATFORM_KEY);
      const returnTo = sessionStorage.getItem(SOCIAL_OAUTH_RETURN_TO_KEY) ?? ROUTES.socialAccounts;

      if (error) {
        setStatus("Connection was denied.");
        toast({
          title: "Connection denied",
          description: "The platform did not authorize this connection.",
        });
        router.replace(returnTo);
        return;
      }

      if (!code || !state || !storedState || !codeVerifier || !platformCode) {
        setStatus("Connection could not be completed.");
        toast({
          title: "Connection failed",
          description: "Missing OAuth callback parameters.",
        });
        router.replace(returnTo);
        return;
      }

      if (state !== storedState) {
        setStatus("Connection could not be completed.");
        toast({
          title: "Connection failed",
          description: "OAuth state mismatch.",
        });
        router.replace(returnTo);
        return;
      }

      try {
        await socialAccountService.connectAccount({
          platformCode,
          authorizationCode: code,
          codeVerifier,
          redirectUri: `${window.location.origin}${ROUTES.socialCallback}`,
          state,
        });
        sessionStorage.removeItem(SOCIAL_OAUTH_STATE_KEY);
        sessionStorage.removeItem(SOCIAL_OAUTH_VERIFIER_KEY);
        sessionStorage.removeItem(SOCIAL_OAUTH_PLATFORM_KEY);
        sessionStorage.removeItem(SOCIAL_OAUTH_RETURN_TO_KEY);
        toast({
          title: "Account connected",
          description: "Your social account is ready for publishing.",
        });
        router.replace(returnTo);
      } catch (connectError) {
        setStatus("Connection failed.");
        toast({
          title: "Connection failed",
          description: resolveSocialAccountErrorMessage(connectError),
        });
        router.replace(returnTo);
      }
    }

    void completeSocialOAuth();
  }, [router, searchParams, toast]);

  return <p className="text-muted-foreground text-sm">{status}</p>;
}

export default function SocialCallbackPage(): React.JSX.Element {
  return (
    <main className="bg-background flex min-h-dvh items-center justify-center p-6">
      <React.Suspense fallback={<p className="text-muted-foreground text-sm">Loading…</p>}>
        <SocialCallbackHandler />
      </React.Suspense>
    </main>
  );
}
