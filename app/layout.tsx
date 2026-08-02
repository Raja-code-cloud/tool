import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { ThemeProvider } from "@/components/theme/theme-provider";
import { SkipLink } from "@/components/layout";
import { AppToastProvider } from "@/hooks/use-toast";
import { WORKSPACE } from "@/constants/workspace";
import "@/styles/globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });

export const metadata: Metadata = {
  title: { default: WORKSPACE.name, template: `%s · ${WORKSPACE.shortName}` },
  description: WORKSPACE.description,
  applicationName: WORKSPACE.name,
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>): React.JSX.Element {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={inter.variable}>
        <ThemeProvider defaultTheme="dark">
          <AppToastProvider>
            <SkipLink />
            {children}
          </AppToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
