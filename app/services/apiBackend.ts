/**
 * Real Backend API Service for React Frontend
 * Replaces mockBackend.ts with actual API calls
 */
import axios from 'axios';
import { Candidate, JobDescription } from '../types';

// API base URL - uses Vite proxy in development
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Helper to generate random delays (for UI consistency)
export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Upload and parse a Job Description file
 */
export const parseJD = async (file: File): Promise<JobDescription> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<JobDescription>('/upload/job', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
};

/**
 * Upload and parse a CV file
 * Returns extracted CV data
 */
export const parseCV = async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/upload/cv', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data.extractedData;
};

/**
 * Match a CV against a Job Description
 * Returns comprehensive candidate analysis
 */
export const matchCVtoJD = async (cvData: any, jdData: any): Promise<Candidate> => {
    const response = await apiClient.post<Candidate>('/match', {
        cv_data: cvData,
        jd_data: jdData,
    });

    return response.data;
};

/**
 * Index a CV for RAG-based Q&A
 */
/**
 * Index a CV for RAG-based Q&A
 */
export const indexCVforRAG = async (
    candidateId: string,
    candidateName: string,
    cvText: string,
    jobId?: string
): Promise<void> => {
    await apiClient.post('/rag/index', {
        candidateId,
        candidateName,
        cvText,
        jobId
    });
};

/**
 * Query indexed CV using RAG
 */
export const queryRAG = async (
    candidateId: string,
    candidateName: string,
    query: string,
    persona: 'recruiter' | 'candidate' = 'recruiter',
    jobId?: string
): Promise<{ answer: string; sources: string[]; source_metadata?: Array<{ name: string; type: string; preview?: string }> }> => {
    await delay(1500); // Add slight delay for better UX

    const response = await apiClient.post<{ answer: string; sources?: string[]; source_metadata?: Array<{ name: string; type: string; preview?: string }> }>('/rag/query', {
        candidateId,
        candidateName,
        query,
        persona,
        jobId
    });

    return {
        answer: response.data.answer,
        sources: response.data.sources || [],
        source_metadata: response.data.source_metadata
    };
};

/**
 * Query all CVs for a specific job description
 */
export const queryAllCVsForJob = async (
    jobId: string,
    query: string,
    persona: 'recruiter' | 'candidate' = 'recruiter'
): Promise<{ answer: string; sources: string[] }> => {
    await delay(1500);

    const response = await apiClient.post<{ answer: string; sources?: string[] }>('/rag/query-all-cvs', {
        jobId,
        query,
        persona
    });

    return {
        answer: response.data.answer,
        sources: response.data.sources || []
    };
};

/**
 * Query all candidates with database integration
 */
export const queryAllCandidates = async (
    query: string,
    jobId?: string,
    persona: 'recruiter' | 'candidate' = 'recruiter'
): Promise<{ answer: string; sources: string[]; candidates_found: number; database_data_included: boolean }> => {
    await delay(1500);

    const response = await apiClient.post('/rag/query-all-candidates', {
        query,
        jobId,
        persona
    });

    return response.data;
};

/**
 * Generate CV summary
 */
export const summarizeCV = async (cvText: string): Promise<string> => {
    const response = await apiClient.post<{ summary: string }>('/summarize/cv', {
        cv_text: cvText,
    });

    return response.data.summary;
};

/**
 * Generate Job Description summary
 */
export const summarizeJD = async (jdText: string): Promise<string> => {
    const response = await apiClient.post<{ summary: string }>('/summarize/jd', {
        jd_text: jdText,
    });

    return response.data.summary;
};

/**
 * Generate match analysis summary (strengths/weaknesses)
 */
export const analyzeMatch = async (
    cvText: string,
    jdText: string,
    matchedSkills: string[],
    missingSkills: string[]
): Promise<string> => {
    const response = await apiClient.post<{ summary: string }>('/summarize/analysis', {
        cv_text: cvText,
        jd_text: jdText,
        matched_skills: matchedSkills,
        missing_skills: missingSkills,
    });

    return response.data.summary;
};

// Export all functions with the same names as mockBackend for easy replacement
export const mockParseJD = parseJD;
export const mockParseCV = parseCV;
export const mockRAGQuery = queryRAG;

// ==================== Database Management APIs ====================

/**
 * Get overall database statistics
 */
export const getDatabaseStats = async (): Promise<any> => {
    const response = await apiClient.get('/database/stats');
    return response.data;
};

/**
 * List all collections in the database
 */
export const getCollections = async (): Promise<any> => {
    const response = await apiClient.get('/database/collections');
    return response.data;
};

/**
 * Get documents from a specific collection
 */
export const getCollectionDocuments = async (
    collectionName: string,
    limit: number = 100
): Promise<any> => {
    const response = await apiClient.get(`/database/collections/${collectionName}/documents`, {
        params: { limit },
    });
    return response.data;
};

/**
 * Clear all documents from a collection
 */
export const clearCollection = async (collectionName: string): Promise<any> => {
    const response = await apiClient.delete(`/database/collections/${collectionName}`);
    return response.data;
};

/**
 * Get information about a specific collection
 */
export const getCollectionInfo = async (collectionName: string): Promise<any> => {
    const response = await apiClient.get(`/database/collections/${collectionName}`);
    return response.data;
};

// ==================== Candidate Management APIs ====================

/**
 * Get all candidates from database
 */
export const getAllCandidates = async (): Promise<Candidate[]> => {
    const response = await apiClient.get('/candidates');
    return response.data;
};

/**
 * Get specific candidate by ID
 */
export const getCandidate = async (candidateId: string): Promise<Candidate> => {
    const response = await apiClient.get(`/candidates/${candidateId}`);
    return response.data;
};

/**
 * Delete a candidate
 */
export const deleteCandidate = async (candidateId: string): Promise<any> => {
    const response = await apiClient.delete(`/candidates/${candidateId}`);
    return response.data;
};

/**
 * Get all job descriptions from database
 */
export const getAllJobDescriptions = async (): Promise<JobDescription[]> => {
    const response = await apiClient.get('/candidates/job-descriptions/all');
    return response.data;
};
