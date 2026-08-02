import Link from "next/link";
import { Compass } from "lucide-react";

import { PageContainer } from "@/components/layout";
import { EmptyState } from "@/components/feedback";
import { Button } from "@/components/ui";
import { ROUTES } from "@/constants/navigation";

export default function NotFound(): React.JSX.Element {
  return (
    <main id="main-content" tabIndex={-1} className="grid min-h-dvh place-items-center p-4 outline-none">
      <PageContainer>
        <EmptyState
          icon={<Compass aria-hidden="true" />}
          title="Page not found"
          description="The page you requested does not exist or may have been moved."
          action={
            <Button asChild>
              <Link href={ROUTES.dashboard}>Back to dashboard</Link>
            </Button>
          }
        />
      </PageContainer>
    </main>
  );
}
