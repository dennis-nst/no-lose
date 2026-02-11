import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    if (apiUrl?.startsWith("http")) {
      const target = apiUrl.replace(/\/api\/?$/, "");
      return [{ source: "/api/:path*", destination: `${target}/api/:path*` }];
    }
    return [];
  },
};

export default nextConfig;
