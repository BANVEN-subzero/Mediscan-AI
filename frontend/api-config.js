// api-config.js
// MediScan AI - Global API Base Configuration

const API_BASE = (() => {
    // 1. Check for manual override in localStorage (great for testing or dynamic configuration)
    const savedUrl = localStorage.getItem('MEDISCAN_API_URL');
    if (savedUrl && savedUrl !== 'undefined') return savedUrl;
    const { protocol, hostname, origin } = window.location;

    // Use Render backend for production (Vercel deployment)
    return 'https://mediscan-ai-2-by4n.onrender.com';
})();

console.log('MediScan API Base configured to:', API_BASE);
