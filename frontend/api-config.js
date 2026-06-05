// api-config.js
// MediScan AI - Global API Base Configuration

// Replace this with YOUR actual Render backend URL once deployed!
const DEPLOYED_BACKEND_URL = 'https://mediscan-ai-2-by4n.onrender.com';

const API_BASE = (() => {
    // 1. Check for manual override in localStorage (great for testing or dynamic configuration)
    const savedUrl = localStorage.getItem('MEDISCAN_API_URL');
    if (savedUrl && savedUrl !== 'undefined') return savedUrl;
    const { protocol, hostname, origin } = window.location;

    // 2. If opening static files directly, backend is usually local on port 8000
    if (protocol === 'file:') {
        // If we are served from Nginx (port 80) or local python simple server, point to local backend (port 8000)
        return 'http://127.0.0.1:8000';
    }
    // 3. Localhost frontend (python http.server, or local browser access)
    // Use explicit backend port to avoid relying on reverse proxy configuration.
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://127.0.0.1:8000';
    }

    // 4. Deployed frontend (Vercel, etc.) - use the deployed Render backend
    return DEPLOYED_BACKEND_URL;
})();

console.log('MediScan API Base configured to:', API_BASE);
