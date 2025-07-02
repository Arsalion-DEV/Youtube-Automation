/** @type {import(next).NextConfig} */
const nextConfig = {
  experimental: {
    optimizeCss: true,
    turbo: {
      rules: {
        "*.svg": {
          loaders: ["@svgr/webpack"],
          as: "*.js",
        },
      },
    },
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === "production",
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },
  images: {
    domains: ["localhost", "13.60.77.139"],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://13.60.77.139:8001",
  },
};

module.exports = nextConfig;
