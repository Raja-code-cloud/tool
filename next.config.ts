import type { NextConfig } from "next";

import { buildSecurityHeaders } from "./lib/security/headers";

const isDev = process.env.NODE_ENV !== "production";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  experimental: {
    optimizePackageImports: ["lucide-react", "recharts", "framer-motion"],
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [...buildSecurityHeaders(isDev)],
      },
    ];
  },
};

export default nextConfig;
