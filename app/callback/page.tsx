"use client";

import { useRouter, useSearchParams } from "next/navigation";
import * as React from "react";

import { ROUTES } from "@/constants/navigation";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import {
  OAUTH_PROVIDER_KEY,
  OAUTH_RETURN_TO_KEY,
  OAUTH_STATE_KEY,
  OAUTH_VERIFIER_KEY,
} from "@/lib/auth/oauth-storage";
import { authService } from "@/lib/services";

function CallbackHandler(): React.JSX.Element {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshSession } = useAuth();
  const { toast } = useToast();
  const [status, setStatus] = React.useState("Completing sign in…");

  React.useEffect(() => {
    async function completeOAuth(): Promise<void> {
      const code = searchParams.get("code");
      const state = searchParams.get("state");
      const storedState = sessionStorage.getItem(OAUTH_STATE_KEY);
      const codeVerifier = sessionStorage.getItem(OAUTH_VERIFIER_KEY);
      const providerCode = sessionStorage.getItem(OAUTH_PROVIDER_KEY);
      const returnTo = sessionStorage.getItem(OAUTH_RETURN_TO_KEY) ?? ROUTES.dashboard;

      if (!code || !state || !storedState || !codeVerifier || !providerCode) {
        setStatus("Sign in could not be completed.");
        toast({
          title: "Sign in failed",
          description: "Missing OAuth callback parameters.",
          variant: "destructive",
        });
        router.replace(ROUTES.login);
        return;
      }

      if (state !== storedState) {
        setStatus("Sign in could not be completed.");
        toast({
          title: "Sign in failed",
          description: "OAuth state mismatch.",
          variant: "destructive",
        });
        router.replace(ROUTES.login);
        return;
      }

      try {
        await authService.login({
          kind: "oauth",
          providerCode,
          authorizationCode: code,
          codeVerifier,
          redirectUri: `${window.location.origin}${ROUTES.callback}`,
          state,
        });
        sessionStorage.removeItem(OAUTH_STATE_KEY);
        sessionStorage.removeItem(OAUTH_VERIFIER_KEY);
        sessionStorage.removeItem(OAUTH_PROVIDER_KEY);
        sessionStorage.removeItem(OAUTH_RETURN_TO_KEY);
        await refreshSession();
        router.replace(returnTo);
      } catch (error) {
        setStatus("Sign in failed.");
        toast({
          title: "Sign in failed",
          description: error instanceof Error ? error.message : "Unable to complete sign in.",
          variant: "destructive",
        });
        router.replace(ROUTES.login);
      }
    }

    void completeOAuth();
  }, [refreshSession, router, searchParams, toast]);

  return <p className="text-muted-foreground text-sm">{status}</p>;
}

export default function CallbackPage(): React.JSX.Element {
  return (
    <main className="bg-background flex min-h-dvh items-center justify-center p-6">
      <React.Suspense fallback={<p className="text-muted-foreground text-sm">Loading…</p>}>
        <CallbackHandler />
      </React.Suspense>
    </main>
  );
}
