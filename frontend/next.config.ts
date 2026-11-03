import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      { source: "/compare", destination: "/teams", permanent: true },
      { source: "/methodology", destination: "/method", permanent: true },
    ];
  },
};

export default nextConfig;
