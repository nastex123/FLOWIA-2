import type { UserProfile, DocumentItem, DocumentDetail, Organization, CheckSummary } from './types';

const API_BASE = '/api/v1';

// Demo mode: when true, use mock data instead of real API
let demoMode = false;

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('flowmind_token') : null;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options?.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    // Auto-clear invalid/expired tokens
    if (response.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('flowmind_token');
    }
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  isDemoMode(): boolean {
    return demoMode || (typeof window !== 'undefined' && localStorage.getItem('flowmind_demo') === 'true');
  },

  setDemoMode(enabled: boolean) {
    demoMode = enabled;
    if (typeof window !== 'undefined') {
      if (enabled) {
        localStorage.setItem('flowmind_demo', 'true');
      } else {
        localStorage.removeItem('flowmind_demo');
      }
    }
  },

  async getProfile() {
    if (this.isDemoMode()) {
      return null;
    }
    return request<UserProfile>('/auth/me');
  },

  async listDocuments() {
    if (this.isDemoMode()) {
      const { mockDocuments } = await import('./mock-data');
      return mockDocuments;
    }
    return request<DocumentItem[]>('/documents');
  },

  async getDocument(id: string) {
    if (this.isDemoMode()) {
      const { mockDocumentDetails } = await import('./mock-data');
      const detail = mockDocumentDetails[id];
      if (!detail) {
        throw new Error('Documento no encontrado en modo demo');
      }
      return detail;
    }
    return request<DocumentDetail>(`/documents/${id}`);
  },

  async uploadDocument(file: File) {
    if (this.isDemoMode()) {
      // Simulate upload in demo mode
      return {
        document_id: 'doc_mock_new',
        filename: file.name,
        status: 'processed',
        message: 'Archivo procesado en modo demo',
      };
    }

    const formData = new FormData();
    formData.append('file', file);

    const token = typeof window !== 'undefined' ? localStorage.getItem('flowmind_token') : null;
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  },

  async reviewDocument(documentId: string, reviewNotes: string) {
    if (this.isDemoMode()) {
      return { status: 'reviewed', document_id: documentId, notes: reviewNotes };
    }
    return request(`/documents/${documentId}/review`, {
      method: 'POST',
      body: JSON.stringify({ review_notes: reviewNotes }),
    });
  },

  getOrganization(): string {
    if (typeof window === 'undefined') return 'default-org';
    return localStorage.getItem('flowmind_org') || 'default-org';
  },

  setOrganization(orgId: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('flowmind_org', orgId);
    }
  },

  async login(email: string, password: string) {
    const data = await request<{ access_token: string; user: { id: string; email: string } }>(
      '/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }
    );

    if (typeof window !== 'undefined') {
      localStorage.setItem('flowmind_token', data.access_token);
    }

    return data;
  },

  async register(email: string, password: string, organization_name?: string) {
    const data = await request<{ access_token: string; user: { id: string; email: string } }>(
      '/auth/register',
      {
        method: 'POST',
        body: JSON.stringify({ email, password, organization_name }),
      }
    );

    if (typeof window !== 'undefined') {
      localStorage.setItem('flowmind_token', data.access_token);
    }

    return data;
  },

  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('flowmind_token');
      localStorage.removeItem('flowmind_org');
      localStorage.removeItem('flowmind_demo');
    }
    demoMode = false;
  },
};
