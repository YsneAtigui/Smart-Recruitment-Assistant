export type Role = 'recruiter' | 'candidate' | null;

export interface Skill {
  name: string;
  category: 'technical' | 'soft' | 'tool';
  proficiency?: number; // 0-100
}

export interface Candidate {
  id: string;
  name: string;
  email: string;
  matchScore: number;
  grade: 'A+' | 'A' | 'B' | 'C' | 'D';
  scores: {
    semantic: number;
    skills: number;
    experience: number;
    education: number;
  };
  matchedSkills: string[];
  missingSkills: string[];
  allSkills?: string[];  // All skills from CV
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  summary: string;
  experienceYears: number;
  role: string;
  experience?: string[];
  education?: string[];
  jobTitle?: string;  // Job description title
}

export interface JobDescription {
  id: string;
  title: string;
  company: string;
  requiredSkills: string[];
  minExperience: number;
  rawText: string;
}

export interface SourceInfo {
  name: string;
  type: 'cv' | 'job_description';
  preview?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  sources?: string[];  // Legacy text sources
  source_metadata?: SourceInfo[];  // New structured sources
  timestamp: Date;
}

export type ViewState = 'landing' | 'upload' | 'dashboard' | 'analysis' | 'rag';

// ==================== Database Management Types ====================

export interface CollectionInfo {
  name: string;
  document_count: number;
  metadata?: Record<string, any>;
  exists?: boolean;
}

export interface DatabaseStats {
  total_collections: number;
  total_documents: number;
  collections: CollectionInfo[];
  persist_directory?: string;
}

export interface IndexedDocument {
  id: string;
  metadata: Record<string, any>;
  preview?: string;
}

