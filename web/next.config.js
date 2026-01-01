/** @type {import('next').NextConfig} */
const nextConfig = {
  // SSR mode - no static export
  images: {
    unoptimized: true,
  },
}

module.exports = nextConfig
