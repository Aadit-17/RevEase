import { Review, ReviewCreate } from '../data/mockData';

// Use environment variable for API base URL, with fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper to get session ID from cookie
export const getSessionId = (): string | null => {
    const match = document.cookie.match(new RegExp('(^| )session_id=([^;]+)'));
    return match ? match[2] : null;
};

// Helper to set session ID in cookie
export const setSessionId = (sessionId: string): void => {
    const expiration = new Date();
    expiration.setTime(expiration.getTime() + 30 * 60 * 1000); // 30 minutes
    document.cookie = `session_id=${sessionId}; expires=${expiration.toUTCString()}; path=/`;
};

// Helper to ensure session ID exists
export const ensureSessionId = (): string => {
    let sessionId = getSessionId();
    if (!sessionId) {
        // Generate new UUIDv4
        sessionId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
        setSessionId(sessionId);
    }
    return sessionId;
};

// API helper function
const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
    const sessionId = ensureSessionId();

    const defaultHeaders = {
        'Content-Type': 'application/json',
        'X-Session-Id': sessionId,
    };

    const config: RequestInit = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        // API request failed
        throw error;
    }
};

// Health check
export const healthCheck = async () => {
    return apiRequest('/health');
};

// Ingest reviews
export const ingestReviews = async (reviews: ReviewCreate[]) => {
    return apiRequest('/ingest', {
        method: 'POST',
        body: JSON.stringify(reviews),
    });
};

// List reviews
export const listReviews = async (
    location?: string,
    sentiment?: string,
    topic?: string,
    q?: string,
    page: number = 1,
    pageSize: number = 10
) => {
    const params = new URLSearchParams();
    if (location) params.append('location', location);
    if (sentiment) params.append('sentiment', sentiment);
    if (topic && topic !== 'all') params.append('topic', topic);
    if (q) params.append('q', q);
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());

    const queryString = params.toString() ? `?${params.toString()}` : '';
    return apiRequest(`/reviews${queryString}`);
};

// Get review by ID
export const getReview = async (id: number) => {
    return apiRequest(`/reviews/${id}`);
};

// Suggest reply for review
export const suggestReply = async (id: number) => {
    return apiRequest(`/reviews/${id}/suggest-reply`, {
        method: 'POST',
    });
};

// Get analytics
export const getAnalytics = async () => {
    return apiRequest('/analytics');
};

// Search reviews
export const searchReviews = async (query: string) => {
    if (!query.trim()) {
        return [];
    }
    const results = await apiRequest(`/search?q=${encodeURIComponent(query)}`);
    // Ensure we return an array of reviews
    return Array.isArray(results) ? results : [];
};