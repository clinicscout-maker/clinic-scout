/** @type {import('next').NextConfig} */
const nextConfig = {
    // Deployment configuration
    output: 'standalone',

    typescript: {
        // Allow production builds to complete even with type errors
        ignoreBuildErrors: true,
    },
    eslint: {
        // Allow production builds to complete even with ESLint errors
        ignoreDuringBuilds: true,
    },
    images: {
        // Enable image optimization
        remotePatterns: [],
    },
    // Enable React strict mode for better development experience
    reactStrictMode: true,

    // Disable static optimization for pages that need runtime env vars
    experimental: {
        serverActions: {
            bodySizeLimit: '2mb',
        },
    },
};

module.exports = nextConfig;
