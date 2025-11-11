/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@get-a-job/shared-types'],
  // Skip static optimization for all pages (they're all dynamic)
  output: 'standalone',
};

module.exports = nextConfig;

