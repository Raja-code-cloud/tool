"use client";

import { CloudLightning } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import * as React from "react";

import { PrimaryButton } from "@/components/buttons/buttons";
import { Card, CardHeader } from "@/components/cards/cards";
import { Input, Label } from "@/components/ui";
import { ROUTES } from "@/constants/navigation";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import {
  OAUTH_PROVIDER_KEY,
  OAUTH_RETURN_TO_KEY,
  OAUTH_STATE_KEY,
  OAUTH_VERIFIER_KEY,
} from "@/lib/auth/oauth-storage";
import { authService, isBackendAuthEnabled } from "@/lib/services";

function LoginForm(): React.JSX.Element {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshSession } = useAuth();
  const { toast } = useToast();
  const [email, setEmail] = React.useState("");
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [providers, setProviders] = React.useState<
    readonly { code: string; name: string; pkceRequired: boolean }[]
  >([]);

  const returnTo = searchParams.get("returnTo") ?? ROUTES.dashboard;

  React.useEffect(() => {
    void authService.listProviders().then(setProviders).catch(() => {});
  }, []);

  const handleMockLogin = React.useCallback(
    async (event: React.FormEvent) => {
      event.preventDefault();
      if (!email.trim()) return;

      setIsSubmitting(true);
      try {
        await authService.login({
          kind: "mock",
          providerCode: "mock",
          email: email.trim(),
          redirectUri: `${window.location.origin}${ROUTES.callback}`,
        });
        await refreshSession();
        router.replace(returnTo);
      } catch (error) {
        toast({
          title: "Sign in failed",
          description: error instanceof Error ? error.message : "Unable to sign in.",
        });
      } finally {
        setIsSubmitting(false);
      }
    },
    [email, refreshSession, returnTo, router, toast],
  );

  const handleOAuthLogin = React.useCallback(
    async (providerCode: string) => {
      setIsSubmitting(true);
      try {
        const redirectUri = `${window.location.origin}${ROUTES.callback}`;
        const flow = await authService.beginAuthorization(providerCode, redirectUri);
        sessionStorage.setItem(OAUTH_STATE_KEY, flow.state);
        sessionStorage.setItem(OAUTH_VERIFIER_KEY, flow.codeVerifier);
        sessionStorage.setItem(OAUTH_PROVIDER_KEY, flow.providerCode);
        sessionStorage.setItem(OAUTH_RETURN_TO_KEY, returnTo);

        if (flow.authorizationUrl.startsWith("mock://")) {
          await authService.login({
            kind: "oauth",
            providerCode: flow.providerCode,
            authorizationCode: `mock-${email.trim().split("@")[0] || "user"}`,
            codeVerifier: flow.codeVerifier,
            redirectUri,
            state: flow.state,
          });
          await refreshSession();
          router.replace(returnTo);
          return;
        }

        window.location.href = flow.authorizationUrl;
      } catch (error) {
        toast({
          title: "Sign in failed",
          description: error instanceof Error ? error.message : "Unable to start sign in.",
        });
      } finally {
        setIsSubmitting(false);
      }
    },
    [email, refreshSession, returnTo, router, toast],
  );

  return (
    <Card className="w-full max-w-md shadow-lg">
      <div className="flex items-center gap-3">
        <span
          aria-hidden="true"
          className="bg-primary text-primary-foreground grid size-10 shrink-0 place-items-center rounded-lg"
        >
          <CloudLightning className="size-5" />
        </span>
        <CardHeader
          title="Sign in"
          description={
            isBackendAuthEnabled
              ? "Use your workspace credentials to continue."
              : "Development mode — mock authentication."
          }
          className="mb-0 flex-1"
        />
      </div>

      <form onSubmit={handleMockLogin} className="mt-6 space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="you@company.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </div>
        <PrimaryButton type="submit" className="w-full" isLoading={isSubmitting}>
          Sign in
        </PrimaryButton>
      </form>

      {providers.length > 0 && (
        <div className="mt-6 space-y-3">
          <p className="text-muted-foreground text-center text-xs font-semibold tracking-wide uppercase">
            Or continue with
          </p>
          {providers
            .filter((provider) => provider.code !== "mock" || isBackendAuthEnabled)
            .map((provider) => (
              <PrimaryButton
                key={provider.code}
                type="button"
                variant="secondary"
                className="w-full"
                isLoading={isSubmitting}
                onClick={() => void handleOAuthLogin(provider.code)}
              >
                {provider.name}
              </PrimaryButton>
            ))}
        </div>
      )}

      <p className="text-muted-foreground mt-6 text-center text-xs">
        By signing in you agree to the workspace terms.{" "}
        <Link href={ROUTES.dashboard} className="text-primary underline-offset-4 hover:underline">
          Back to app
        </Link>
      </p>
    </Card>
  );
}

export default function LoginPage(): React.JSX.Element {
  return (
    <main className="bg-background flex min-h-dvh items-center justify-center p-6">
      <React.Suspense
        fallback={<div className="text-muted-foreground text-sm">Loading sign in…</div>}
      >
        <LoginForm />
      </React.Suspense>
    </main>
  );
}
