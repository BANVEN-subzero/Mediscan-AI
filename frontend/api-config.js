// api-config.js
// MediScan AI - Global API Base Configuration

const API_BASE = (() => {
    // 1. Check for manual override in localStorage (great for testing or dynamic configuration)
    const savedUrl = localStorage.getItem('MEDISCAN_API_URL');
    if (savedUrl && savedUrl !== 'undefined') return savedUrl;

    // 2. Check if we're running locally (development or local docker compose)
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        // If we are served from Nginx (port 80) or local python simple server, point to local backend (port 8000)
        return 'http://127.0.0.1:8000';
    }

    // 3. Fallback / Production environment
    // If the frontend is hosted on Vercel or another platform, it needs to hit the live backend API.
    // Replace this with your production backend API URL (e.g. on Render, Railway, AWS, etc.)
    return 'https://mediscan-backend.onrender.com'; 
})();

console.log('MediScan API Base configured to:', API_BASE);
