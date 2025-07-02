import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    unoptimized: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Remove standalone output for proper button functionality
  experimental: {
    turbo: {
      rules: {}
    }
  }
};

export default nextConfig;
