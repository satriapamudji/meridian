/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    // Disable build workers (child_process.fork + IPC) to keep `next build` compatible
    // with restricted environments where IPC spawning is not permitted.
    webpackBuildWorker: false,
  },
};

module.exports = nextConfig;
