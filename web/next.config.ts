import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // transformers.js is browser-only in this app
  serverExternalPackages: ["@huggingface/transformers"],
};

export default nextConfig;
