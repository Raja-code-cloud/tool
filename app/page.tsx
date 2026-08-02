import { redirect } from "next/navigation";

import { ROUTES } from "@/constants/navigation";

/** `/` has no interface of its own; the dashboard is the workspace entry point. */
export default function RootPage(): never {
  redirect(ROUTES.dashboard);
}
