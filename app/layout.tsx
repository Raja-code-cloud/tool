import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { SkipLink } from "@/components/layout";
import { ThemeProvider } from "@/components/theme/theme-provider";
import { WORKSPACE } from "@/constants/workspace";
import { AuthProvider } from "@/hooks/use-auth";
import { AppToastProvider } from "@/hooks/use-toast";

import "@/styles/globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });

const workspace = WORKSPACE;

export const metadata: Metadata = {
  title: { default: workspace.name, template: `%s · ${workspace.shortName}` },
  description: workspace.description,
  applicationName: workspace.name,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>): React.JSX.Element {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={inter.variable}>
        <ThemeProvider defaultTheme="dark">
          <AppToastProvider>
            <AuthProvider>
              <SkipLink />
              {children}
            </AuthProvider>
          </AppToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
