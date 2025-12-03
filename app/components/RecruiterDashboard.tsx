import React, { useState, useEffect } from 'react';
import {
  UploadCloud,
  Target,
  BarChart3,
  MessageSquare,
  ChevronRight,
  Search,
  User,
  ArrowLeft,
  Loader2,
  FileText,
  X,
  Copy,
  AlertTriangle,
  Database,
  Trash2,
  RefreshCw
} from './ui/Icons';
import { FileUpload } from './ui/FileUpload';
import { parseCV, parseJD, matchCVtoJD, queryRAG, indexCVforRAG, getDatabaseStats, getCollections, getCollectionDocuments, clearCollection, summarizeCV, getAllCandidates, deleteCandidate, queryAllCandidates, queryAllCVsForJob } from '../services/apiBackend';
import { Candidate, JobDescription, ChatMessage, DatabaseStats, CollectionInfo } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend } from 'recharts';

interface RecruiterDashboardProps {
  onBack: () => void;
}

type Tab = 'upload' | 'results' | 'analytics' | 'rag' | 'candidates';

export const RecruiterDashboard: React.FC<RecruiterDashboardProps> = ({ onBack }) => {
  const [activeTab, setActiveTab] = useState<Tab>('upload');
  const [jdFile, setJdFile] = useState<JobDescription | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [allCandidates, setAllCandidates] = useState<Candidate[]>([]);  // All candidates from DB
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Comparison State
  const [comparisonIds, setComparisonIds] = useState<string[]>([]);
  const [isComparisonOpen, setIsComparisonOpen] = useState(false);

  // RAG State
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [queryMode, setQueryMode] = useState<'specific' | 'all-job' | 'all-database'>('all-job'); // Query mode for RAG

  // Database Management State
  const [dbStats, setDbStats] = useState<DatabaseStats | null>(null);
  const [showDbPanel, setShowDbPanel] = useState(false);
  const [dbLoading, setDbLoading] = useState(false);
  const [indexingNotification, setIndexingNotification] = useState<string | null>(null);

  // Fetch database stats when RAG tab is active
  useEffect(() => {
    if (activeTab === 'rag') {
      fetchDatabaseStats();
    }
  }, [activeTab]);

  // Fetch all candidates when Candidates tab is active
  useEffect(() => {
    if (activeTab === 'candidates') {
      fetchAllCandidates();
    }
  }, [activeTab]);

  const fetchAllCandidates = async () => {
    try {
      setDbLoading(true);
      const candidatesData = await getAllCandidates();
      setAllCandidates(candidatesData);
    } catch (err) {
      console.error('Failed to fetch candidates:', err);
    } finally {
      setDbLoading(false);
    }
  };

  const fetchDatabaseStats = async () => {
    try {
      setDbLoading(true);
      const stats = await getDatabaseStats();
      setDbStats(stats);
    } catch (err) {
      console.error('Failed to fetch database stats:', err);
    } finally {
      setDbLoading(false);
    }
  };

  const handleClearCollection = async (collectionName: string) => {
    if (!confirm(`Are you sure you want to clear collection "${collectionName}"? This cannot be undone.`)) {
      return;
    }

    try {
      setDbLoading(true);
      await clearCollection(collectionName);
      await fetchDatabaseStats();
      alert(`Collection "${collectionName}" cleared successfully!`);
    } catch (err) {
      console.error('Failed to clear collection:', err);
      alert('Failed to clear collection');
    } finally {
      setDbLoading(false);
    }
  };

  const handleProcess = async () => {
    // This function is now mainly for switching tabs as processing happens on upload
    setActiveTab('results');
  };

  const handleFileUploads = async (files: File[], type: 'cv' | 'jd') => {
    setError(null);
    try {
      if (type === 'jd') {
        setIsProcessing(true);
        const data = await parseJD(files[0]);
        setJdFile(data);
        setIndexingNotification('✓ Job description indexed to ChromaDB');
        setTimeout(() => setIndexingNotification(null), 5000);
        setIsProcessing(false);
      } else {
        if (!jdFile) {
          setError("Please upload a Job Description first.");
          return;
        }

        setIsProcessing(true);
        const newCandidates: Candidate[] = [];
        let indexedCount = 0;

        for (const file of files) {
          try {
            // 1. Parse CV
            const cvData = await parseCV(file);

            // 2. Generate CV summary using /summarize/cv endpoint
            const cvSummary = await summarizeCV(cvData.raw_text);

            // 3. Add summary to cvData to pass to backend
            cvData.cv_summary = cvSummary;

            // 4. Match against JD
            const matchResult = await matchCVtoJD(cvData, jdFile);

            // 5. Replace summary with the one from /summarize/cv
            matchResult.summary = cvSummary;

            // 6. Index for RAG (background)
            indexCVforRAG(matchResult.id, matchResult.name, cvData.raw_text, jdFile.id)
              .then(() => {
                indexedCount++;
                setIndexingNotification(`✓ ${indexedCount} CV${indexedCount > 1 ? 's' : ''} indexed to ChromaDB`);
              })
              .catch(console.error);

            newCandidates.push(matchResult);
          } catch (err) {
            console.error(`Error processing file ${file.name}:`, err);
            // Continue with other files
          }
        }

        setCandidates(prev => [...prev, ...newCandidates].sort((a, b) => b.matchScore - a.matchScore));
        setIsProcessing(false);

        // Clear notification after 5 seconds
        setTimeout(() => setIndexingNotification(null), 5000);
      }
    } catch (err) {
      console.error("Upload error:", err);
      setError("An error occurred during processing. Please try again.");
      setIsProcessing(false);
    }
  };

  const toggleComparisonSelection = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setComparisonIds(prev =>
      prev.includes(id) ? prev.filter(cid => cid !== id) : [...prev, id]
    );
  };

  const handleAskQuestion = async () => {
    if (!chatInput.trim()) return;

    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: chatInput,
      timestamp: new Date()
    };

    setChatHistory(prev => [...prev, newMessage]);
    setChatInput("");
    setIsChatLoading(true);

    try {
      let answer: string;
      let sources: string[] = [];
      let sourceMetadata: Array<{ name: string; type: string; preview?: string }> | undefined;

      // Determine which query to use based on mode
      if (queryMode === 'all-database') {
        // Query all candidates with database integration
        const response = await queryAllCandidates(newMessage.text, jdFile?.id, 'recruiter');
        answer = response.answer;
        sources = response.sources;
      } else if (queryMode === 'all-job' && jdFile) {
        // Query all CVs for the specific job
        const response = await queryAllCVsForJob(jdFile.id, newMessage.text, 'recruiter');
        answer = response.answer;
        sources = response.sources;
      } else if (selectedCandidateId) {
        // Query specific candidate
        const candidateName = candidates.find(c => c.id === selectedCandidateId)?.name || "Unknown Candidate";
        const response = await queryRAG(selectedCandidateId, candidateName, newMessage.text, 'recruiter', jdFile?.id);
        answer = response.answer;
        sources = response.sources;
        sourceMetadata = response.source_metadata;
      } else {
        // Default to all-job mode if job is selected
        if (jdFile) {
          const response = await queryAllCVsForJob(jdFile.id, newMessage.text, 'recruiter');
          answer = response.answer;
          sources = response.sources;
        } else {
          // Fallback to all candidates from database
          const response = await queryAllCandidates(newMessage.text, undefined, 'recruiter');
          answer = response.answer;
          sources = response.sources;
        }
      }

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: answer,
        sources: sources,
        timestamp: new Date()
      };

      setChatHistory(prev => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: "Sorry, I encountered an error processing your question.",
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const selectedCandidate = candidates.find(c => c.id === selectedCandidateId);

  // Render Functions
  const renderSidebar = () => (
    <div className="w-64 bg-white border-r border-slate-200 min-h-screen flex flex-col fixed left-0 top-0 bottom-0 z-10">
      <div className="p-6 border-b border-slate-100 flex items-center">
        <div className="h-8 w-8 bg-recruiter-600 rounded-lg mr-3 flex items-center justify-center text-white font-bold">R</div>
        <span className="font-bold text-slate-800">Recruit OS</span>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        <button
          onClick={() => setActiveTab('upload')}
          className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${activeTab === 'upload' ? 'bg-recruiter-50 text-recruiter-700' : 'text-slate-600 hover:bg-slate-50'}`}
        >
          <UploadCloud size={18} className="mr-3" />
          Upload Docs
        </button>
        <button
          onClick={() => setActiveTab('results')}
          disabled={candidates.length === 0}
          className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${activeTab === 'results' ? 'bg-recruiter-50 text-recruiter-700' : 'text-slate-600 hover:bg-slate-50'} ${candidates.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <Target size={18} className="mr-3" />
          Matching Results
          {candidates.length > 0 && <span className="ml-auto bg-recruiter-100 text-recruiter-600 py-0.5 px-2 rounded-full text-xs">{candidates.length}</span>}
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          disabled={candidates.length === 0}
          className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${activeTab === 'analytics' ? 'bg-recruiter-50 text-recruiter-700' : 'text-slate-600 hover:bg-slate-50'} ${candidates.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <BarChart3 size={18} className="mr-3" />
          Analytics
        </button>
        <button
          onClick={() => setActiveTab('rag')}
          disabled={candidates.length === 0}
          className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${activeTab === 'rag' ? 'bg-recruiter-50 text-recruiter-700' : 'text-slate-600 hover:bg-slate-50'} ${candidates.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <MessageSquare size={18} className="mr-3" />
          Ask AI
        </button>
        <button
          onClick={() => setActiveTab('candidates')}
          className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${activeTab === 'candidates' ? 'bg-recruiter-50 text-recruiter-700' : 'text-slate-600 hover:bg-slate-50'}`}
        >
          <User size={18} className="mr-3" />
          All Candidates
          {allCandidates.length > 0 && <span className="ml-auto bg-recruiter-100 text-recruiter-600 py-0.5 px-2 rounded-full text-xs">{allCandidates.length}</span>}
        </button>
      </nav>

      <div className="p-4 border-t border-slate-100">
        <button onClick={onBack} className="flex items-center text-slate-500 hover:text-slate-800 text-sm font-medium">
          <ArrowLeft size={16} className="mr-2" />
          Switch Role
        </button>
      </div>
    </div>
  );

  const renderComparisonModal = () => {
    if (!isComparisonOpen) return null;
    const comparisonCandidates = candidates.filter(c => comparisonIds.includes(c.id));

    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
        <div className="bg-white rounded-xl shadow-2xl w-full max-w-[95vw] max-h-[90vh] flex flex-col overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
            <h3 className="font-bold text-xl text-slate-800 flex items-center">
              <BarChart3 className="mr-2 text-recruiter-600" />
              Compare Candidates ({comparisonCandidates.length})
            </h3>
            <button onClick={() => setIsComparisonOpen(false)} className="p-2 hover:bg-slate-200 rounded-full text-slate-500 transition-colors">
              <X size={24} />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-auto p-6 bg-slate-100">
            <div className="flex gap-6 min-w-max pb-4">
              {comparisonCandidates.map(c => (
                <div key={c.id} className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col w-[350px]">
                  {/* Card Header */}
                  <div className="p-6 border-b border-slate-100 text-center bg-white relative">
                    <button
                      className="absolute top-2 right-2 text-slate-400 hover:text-red-500"
                      onClick={(e) => toggleComparisonSelection(c.id, e)}
                      title="Remove from comparison"
                    >
                      <X size={18} />
                    </button>
                    <div className="w-16 h-16 bg-slate-50 border border-slate-200 rounded-full mx-auto flex items-center justify-center mb-3 shadow-sm text-slate-400">
                      <User size={32} />
                    </div>
                    <h4 className="font-bold text-lg text-slate-900 truncate" title={c.name}>{c.name}</h4>
                    <p className="text-xs text-slate-500 mb-3 truncate" title={c.role}>{c.role}</p>
                    <div className={`inline-flex items-center justify-center px-3 py-1 rounded-full text-white text-sm font-bold shadow-sm ${c.matchScore >= 85 ? 'bg-green-500' : c.matchScore >= 75 ? 'bg-yellow-500' : 'bg-slate-500'}`}>
                      {c.matchScore}% Match
                    </div>
                  </div>

                  {/* Body */}
                  <div className="p-6 space-y-6 flex-1 bg-slate-50/30">
                    {/* Radar */}
                    <div className="h-48 -mx-2">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={[
                          { subject: 'Semantic', A: c.scores.semantic, fullMark: 100 },
                          { subject: 'Skills', A: c.scores.skills, fullMark: 100 },
                          { subject: 'Exp', A: c.scores.experience, fullMark: 100 },
                          { subject: 'Edu', A: c.scores.education, fullMark: 100 },
                        ]}>
                          <PolarGrid />
                          <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fill: '#64748b' }} />
                          <Radar name={c.name} dataKey="A" stroke="#2563eb" fill="#3b82f6" fillOpacity={0.3} />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-2 gap-3 text-center">
                      <div className="p-3 bg-white border border-slate-200 rounded-lg">
                        <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Experience</div>
                        <div className="font-bold text-slate-800">{c.experienceYears} Yrs</div>
                      </div>
                      <div className="p-3 bg-white border border-slate-200 rounded-lg">
                        <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Grade</div>
                        <div className={`font-bold ${c.grade.startsWith('A') ? 'text-green-600' : 'text-slate-800'}`}>{c.grade}</div>
                      </div>
                    </div>

                    {/* Skills */}
                    <div>
                      <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center">
                        <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></span>
                        Matched Skills
                      </h5>
                      <div className="flex flex-wrap gap-1.5">
                        {c.matchedSkills.slice(0, 10).map(s => (
                          <span key={s} className="px-2 py-0.5 bg-green-50 text-green-700 text-[10px] font-medium rounded border border-green-100">{s}</span>
                        ))}
                        {c.matchedSkills.length > 10 && <span className="text-[10px] text-slate-400 self-center">+{c.matchedSkills.length - 10}</span>}
                      </div>
                    </div>

                    <div>
                      <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center">
                        <span className="w-1.5 h-1.5 bg-red-500 rounded-full mr-2"></span>
                        Missing Skills
                      </h5>
                      <div className="flex flex-wrap gap-1.5">
                        {c.missingSkills.length > 0 ? c.missingSkills.slice(0, 8).map(s => (
                          <span key={s} className="px-2 py-0.5 bg-red-50 text-red-700 text-[10px] font-medium rounded border border-red-100">{s}</span>
                        )) : <span className="text-xs text-slate-400 italic">None detected</span>}
                      </div>
                    </div>

                    {/* Summary */}
                    <div>
                      <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Summary</h5>
                      <p className="text-xs text-slate-600 bg-white p-2 rounded border border-slate-200 line-clamp-3" title={c.summary}>
                        {c.summary}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderUpload = () => (
    <div className="max-w-4xl mx-auto py-10 px-4">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Setup Recruitment Pipeline</h2>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center">
          <AlertTriangle className="mr-2" size={20} />
          {error}
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 mb-8">
        <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center">
          <span className="bg-recruiter-100 text-recruiter-600 h-6 w-6 rounded-full flex items-center justify-center text-xs mr-2">1</span>
          Target Job Description
        </h3>
        {jdFile ? (
          <div className="bg-recruiter-50 border border-recruiter-200 rounded-lg p-4 flex items-start">
            <div className="bg-white p-2 rounded-md shadow-sm mr-4">
              <FileText className="text-recruiter-500" />
            </div>
            <div>
              <h4 className="font-bold text-recruiter-900">{jdFile.title}</h4>
              <p className="text-sm text-recruiter-700">{jdFile.company}</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {jdFile.requiredSkills.slice(0, 4).map(skill => (
                  <span key={skill} className="text-xs bg-white text-recruiter-600 px-2 py-1 rounded-md border border-recruiter-200">{skill}</span>
                ))}
              </div>
            </div>
            <button onClick={() => setJdFile(null)} className="ml-auto text-slate-400 hover:text-recruiter-600">Change</button>
          </div>
        ) : (
          <FileUpload label="Upload Job Description" onFilesSelected={(f) => handleFileUploads(f, 'jd')} />
        )}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 mb-8">
        <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center">
          <span className="bg-recruiter-100 text-recruiter-600 h-6 w-6 rounded-full flex items-center justify-center text-xs mr-2">2</span>
          Candidate CVs
        </h3>
        <FileUpload
          label="Upload Candidates (Batch)"
          multiple={true}
          onFilesSelected={(f) => handleFileUploads(f, 'cv')}
        />
        {candidates.length > 0 && (
          <div className="mt-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <p className="text-slate-700 font-medium">{candidates.length} CVs staged for processing</p>
          </div>
        )}

        {isProcessing && (
          <div className="mt-6 space-y-6">
            {/* Main Processing Status */}
            <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-xl p-10 flex flex-col items-center justify-center">
              <Loader2 className="h-10 w-10 text-slate-400 animate-spin mb-4" />
              <p className="text-slate-500 font-medium text-lg">Extracting Candidate Data...</p>
            </div>

            {/* Skeleton Rows */}
            <div className="space-y-4 opacity-50">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white border border-slate-100 rounded-lg p-4 flex items-center shadow-sm">
                  <div className="h-4 w-4 bg-slate-200 rounded-full mr-4"></div>
                  <div className="h-4 bg-slate-100 rounded w-full"></div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleProcess}
          disabled={!jdFile || candidates.length === 0 || isProcessing}
          className={`flex items-center px-8 py-3 rounded-lg text-white font-medium shadow-md transition-all ${!jdFile || candidates.length === 0 ? 'bg-slate-300 cursor-not-allowed' : 'bg-recruiter-600 hover:bg-recruiter-700'
            }`}
        >
          {isProcessing ? (
            <>
              <Loader2 className="animate-spin mr-2" />
              Processing AI Matching...
            </>
          ) : (
            <>
              Analyze & Match Candidates
              <ChevronRight className="ml-2" />
            </>
          )}
        </button>
      </div>
    </div>
  );

  const renderResults = () => {
    if (selectedCandidateId) {
      // Detail View
      return renderCandidateDetail();
    }

    // List View
    return (
      <div className="max-w-6xl mx-auto py-8 px-4">
        <div className="flex justify-between items-end mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-800">Matching Results</h2>
            <p className="text-slate-500">For role: <span className="font-semibold text-slate-700">{jdFile?.title}</span></p>
          </div>

          <div className="flex items-center space-x-4">
            {/* Compare Button */}
            <button
              onClick={() => setIsComparisonOpen(true)}
              disabled={comparisonIds.length < 2}
              className={`flex items-center px-4 py-2 rounded-lg font-medium transition-all ${comparisonIds.length >= 2
                ? 'bg-recruiter-600 text-white shadow-md hover:bg-recruiter-700'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                }`}
            >
              <BarChart3 size={16} className="mr-2" />
              Compare ({comparisonIds.length})
            </button>

            {/* Legend */}
            <div className="hidden md:flex space-x-3 text-sm border-l border-slate-300 pl-4">
              <div className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-green-500 mr-2"></span>Excellent</div>
              <div className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-yellow-500 mr-2"></span>Good</div>
              <div className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-slate-300 mr-2"></span>Fair</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {candidates.map((candidate) => {
            const isExcellent = candidate.matchScore >= 85;
            const isGood = candidate.matchScore >= 75 && candidate.matchScore < 85;
            const borderColor = isExcellent ? 'border-l-4 border-l-green-500' : (isGood ? 'border-l-4 border-l-yellow-400' : 'border-l-4 border-l-slate-300');
            const isSelected = comparisonIds.includes(candidate.id);

            return (
              <div
                key={candidate.id}
                className={`relative bg-white rounded-lg shadow-sm border ${isSelected ? 'border-recruiter-500 ring-1 ring-recruiter-500' : 'border-slate-200'} p-6 flex flex-col md:flex-row items-center hover:shadow-md transition-all cursor-pointer ${borderColor}`}
                onClick={() => setSelectedCandidateId(candidate.id)}
              >
                {/* Checkbox for selection */}
                <div className="mr-4 flex items-center" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={(e) => toggleComparisonSelection(candidate.id, e as unknown as React.MouseEvent)}
                    className="w-5 h-5 rounded border-slate-300 text-recruiter-600 focus:ring-recruiter-500 cursor-pointer"
                  />
                </div>

                <div className="flex-1">
                  <div className="flex items-center mb-1">
                    <h3 className="text-lg font-bold text-slate-900 mr-3">{candidate.name}</h3>
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${isExcellent ? 'bg-green-100 text-green-700' : (isGood ? 'bg-yellow-100 text-yellow-800' : 'bg-slate-100 text-slate-700')}`}>
                      Grade {candidate.grade}
                    </span>
                  </div>
                  <p className="text-slate-500 text-sm mb-3">{candidate.summary}</p>

                  <div className="flex flex-wrap gap-2">
                    {candidate.matchedSkills.slice(0, 5).map(skill => (
                      <span key={skill} className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded border border-green-100 flex items-center">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500 mr-1"></span>
                        {skill}
                      </span>
                    ))}
                    {candidate.missingSkills.slice(0, 2).map(skill => (
                      <span key={skill} className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded border border-red-100 flex items-center">
                        <span className="w-1.5 h-1.5 rounded-full bg-red-500 mr-1"></span>
                        Missing: {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col items-center md:items-end mt-4 md:mt-0 md:ml-6 min-w-[120px]">
                  <div className="text-3xl font-bold text-slate-800">{candidate.matchScore}%</div>
                  <span className="text-xs text-slate-500 uppercase tracking-wide font-medium">Match Score</span>
                  <button className="mt-3 text-recruiter-600 text-sm font-medium hover:underline flex items-center">
                    View Analysis <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderCandidateDetail = () => {
    if (!selectedCandidate) return null;
    return (
      <div className="max-w-6xl mx-auto py-8 px-4">
        <button onClick={() => setSelectedCandidateId(null)} className="mb-6 flex items-center text-slate-500 hover:text-slate-900">
          <ArrowLeft size={16} className="mr-1" /> Back to List
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Profile */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
              <div className="w-20 h-20 bg-slate-100 rounded-full mx-auto flex items-center justify-center mb-4">
                <User size={32} className="text-slate-400" />
              </div>
              <h2 className="text-xl font-bold text-slate-900">{selectedCandidate.name}</h2>


              <div className="mt-6 flex justify-center items-center">
                <div className="relative h-32 w-32 flex items-center justify-center">
                  {/* Simple circular progress visualization using SVG */}
                  <svg className="w-full h-full" viewBox="0 0 36 36">
                    <path
                      className="text-slate-100"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                    />
                    <path
                      className={selectedCandidate.matchScore > 80 ? "text-green-500" : "text-recruiter-500"}
                      strokeDasharray={`${selectedCandidate.matchScore}, 100`}
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-2xl font-bold text-slate-800">{selectedCandidate.matchScore}%</span>
                    <span className="text-xs text-slate-500">MATCH</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-bold text-slate-800 mb-4">Skill Radar</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={[
                    { subject: 'Semantic', A: selectedCandidate.scores.semantic, fullMark: 100 },
                    { subject: 'Skills', A: selectedCandidate.scores.skills, fullMark: 100 },
                    { subject: 'Exp', A: selectedCandidate.scores.experience, fullMark: 100 },
                    { subject: 'Edu', A: selectedCandidate.scores.education, fullMark: 100 },
                  ]}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
                    <Radar name={selectedCandidate.name} dataKey="A" stroke="#2563eb" fill="#3b82f6" fillOpacity={0.4} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Experience */}
            {selectedCandidate.experience && selectedCandidate.experience.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="font-bold text-slate-800 mb-4 flex items-center">
                  <span className="bg-purple-100 p-1 rounded mr-2">💼</span>
                  Experience
                </h3>
                <div className="space-y-3">
                  {selectedCandidate.experience.map((exp, index) => (
                    <div key={index} className="pb-3 border-b border-slate-100 last:border-0 last:pb-0">
                      <p className="text-sm text-slate-700 leading-relaxed">{exp}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Education */}
            {selectedCandidate.education && selectedCandidate.education.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="font-bold text-slate-800 mb-4 flex items-center">
                  <span className="bg-green-100 p-1 rounded mr-2">🎓</span>
                  Education
                </h3>
                <div className="space-y-3">
                  {selectedCandidate.education.map((edu, index) => (
                    <div key={index} className="pb-3 border-b border-slate-100 last:border-0 last:pb-0">
                      <p className="text-sm text-slate-700 leading-relaxed">{edu}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Analysis */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-bold text-slate-800 mb-2 flex items-center"><FileText size={18} className="mr-2 text-recruiter-500" /> AI Summary</h3>
              <p className="text-slate-600 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100">
                {selectedCandidate.summary}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="font-bold text-green-700 mb-4 flex items-center">
                  <span className="bg-green-100 p-1 rounded mr-2"><Target size={14} /></span>
                  Strengths
                </h3>
                <ul className="space-y-2">
                  {selectedCandidate.strengths.map((str, i) => (
                    <li key={i} className="flex items-start text-sm text-slate-700">
                      <span className="mr-2 mt-1 text-green-500">•</span>
                      {str}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="font-bold text-amber-600 mb-4 flex items-center">
                  <span className="bg-amber-100 p-1 rounded mr-2"><Target size={14} /></span>
                  Missing / Weaknesses
                </h3>
                <ul className="space-y-2">
                  {selectedCandidate.weaknesses.map((wk, i) => (
                    <li key={i} className="flex items-start text-sm text-slate-700">
                      <span className="mr-2 mt-1 text-amber-500">•</span>
                      {wk}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-bold text-slate-800 mb-4">Matched Skills</h3>
              <div className="flex flex-wrap gap-2">
                {selectedCandidate.matchedSkills.map(s => (
                  <span key={s} className="px-3 py-1 bg-green-50 text-green-700 border border-green-200 rounded-full text-sm font-medium">{s}</span>
                ))}
              </div>
              <h3 className="font-bold text-slate-800 mt-6 mb-4">Missing Skills</h3>
              <div className="flex flex-wrap gap-2">
                {selectedCandidate.missingSkills.map(s => (
                  <span key={s} className="px-3 py-1 bg-red-50 text-red-700 border border-red-200 rounded-full text-sm font-medium">{s}</span>
                ))}
              </div>
            </div>

            {/* All Skills from CV */}
            {selectedCandidate.allSkills && selectedCandidate.allSkills.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="font-bold text-slate-800 mb-4 flex items-center">
                  <span className="bg-blue-100 p-1 rounded mr-2">⚡</span>
                  All Skills from CV
                  <span className="ml-2 text-sm font-normal text-slate-500">({selectedCandidate.allSkills.length} total)</span>
                </h3>
                <div className="flex flex-wrap gap-2">
                  {selectedCandidate.allSkills.map(s => (
                    <span key={s} className="px-3 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-full text-sm font-medium">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Chat Context */}
            <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex items-center justify-between">
              <div>
                <h4 className="font-bold text-blue-900">Have questions about {selectedCandidate.name}?</h4>
                <p className="text-sm text-blue-700">Use the AI assistant to query their CV specifically.</p>
              </div>
              <button
                onClick={() => {
                  setQueryMode('specific');
                  setActiveTab('rag');
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
              >
                Ask AI
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderAnalytics = () => {
    // Simple mock data aggregation
    const scoreDistribution = [
      { range: '90-100', count: candidates.filter(c => c.matchScore >= 90).length },
      { range: '80-89', count: candidates.filter(c => c.matchScore >= 80 && c.matchScore < 90).length },
      { range: '70-79', count: candidates.filter(c => c.matchScore >= 70 && c.matchScore < 80).length },
      { range: '<70', count: candidates.filter(c => c.matchScore < 70).length },
    ];

    return (
      <div className="max-w-6xl mx-auto py-8 px-4">
        <h2 className="text-2xl font-bold text-slate-800 mb-6">Pipeline Analytics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 className="font-bold text-slate-700 mb-6">Match Score Distribution</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={scoreDistribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 className="font-bold text-slate-700 mb-6">Pipeline Summary</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-slate-50 rounded-lg">
                <span className="text-slate-600">Total Candidates</span>
                <span className="text-2xl font-bold text-slate-900">{candidates.length}</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg">
                <span className="text-green-700">Avg. Match Score</span>
                <span className="text-2xl font-bold text-green-700">
                  {candidates.length > 0
                    ? Math.round(candidates.reduce((acc, c) => acc + c.matchScore, 0) / candidates.length)
                    : 0}%
                </span>
              </div>
              <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
                <span className="text-blue-700">Interview Ready (A Grade)</span>
                <span className="text-2xl font-bold text-blue-700">
                  {candidates.filter(c => c.grade.startsWith('A')).length}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderRAG = () => (
    <div className="flex flex-col h-[calc(100vh-2rem)] max-w-6xl mx-auto py-4 px-4">
      {/* Header with Database Stats */}
      <div className="flex-none mb-4 flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Ask AI Assistant</h2>
          <p className="text-slate-500">Query your candidate pool using natural language.</p>

          {/* Query Mode Indicator */}
          <div className="mt-3 flex items-center gap-2">
            <span className="text-sm text-slate-600 font-medium">Query Mode:</span>
            {queryMode === 'all-database' && (
              <div className="flex items-center gap-2">
                <span className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded-lg border border-purple-200 font-medium">
                  📊 All Candidates (Database + RAG)
                </span>
                <button
                  onClick={() => setQueryMode('all-job')}
                  className="text-xs text-slate-500 hover:text-slate-700 underline"
                >
                  Switch to Job Mode
                </button>
              </div>
            )}
            {queryMode === 'all-job' && jdFile && (
              <div className="flex items-center gap-2">
                <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-lg border border-blue-200 font-medium">
                  💼 All CVs for: <strong>{jdFile.title}</strong>
                </span>
                <button
                  onClick={() => setQueryMode('all-database')}
                  className="text-xs text-slate-500 hover:text-slate-700 underline"
                >
                  Switch to Database Mode
                </button>
              </div>
            )}
            {selectedCandidateId && (
              <div className="flex items-center gap-2">
                <span className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded-lg border border-green-200 font-medium">
                  👤 Specific: <strong>{candidates.find(c => c.id === selectedCandidateId)?.name}</strong>
                </span>
                <button
                  onClick={() => {
                    setSelectedCandidateId(null);
                    setQueryMode('all-job');
                  }}
                  className="text-xs text-slate-500 hover:text-slate-700 underline"
                >
                  Clear
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Database Stats Card */}
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 min-w-[280px]">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold text-slate-700 flex items-center">
              <Database size={18} className="mr-2 text-blue-600" />
              ChromaDB Status
            </h3>
            <button onClick={fetchDatabaseStats} className="p-1 hover:bg-slate-100 rounded" disabled={dbLoading}>
              <RefreshCw size={14} className={`text-slate-500 ${dbLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
          {dbStats ? (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Collections:</span>
                <span className="font-bold text-slate-800">{dbStats.total_collections}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Documents:</span>
                <span className="font-bold text-slate-800">{dbStats.total_documents}</span>
              </div>
              <button
                onClick={() => setShowDbPanel(!showDbPanel)}
                className="w-full mt-2 text-xs text-blue-600 hover:text-blue-700 font-medium"
              >
                {showDbPanel ? 'Hide' : 'Manage'} Collections
              </button>
            </div>
          ) : (
            <div className="text-xs text-slate-400">Loading...</div>
          )}
        </div>
      </div>

      {/* Database Management Panel */}
      {showDbPanel && dbStats && (
        <div className="mb-4 bg-slate-50 rounded-lg border border-slate-200 p-4">
          <h4 className="font-bold text-slate-700 mb-3">Indexed Collections</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-64 overflow-y-auto">
            {dbStats.collections.map((col: CollectionInfo) => (
              <div key={col.name} className="bg-white rounded border border-slate-200 p-3 flex justify-between items-center">
                <div className="flex-1">
                  <div className="font-medium text-slate-800 text-sm truncate" title={col.name}>
                    {col.name}
                  </div>
                  <div className="text-xs text-slate-500">{col.document_count} documents</div>
                </div>
                <button
                  onClick={() => handleClearCollection(col.name)}
                  className="ml-2 p-2 hover:bg-red-50 rounded text-red-600 hover:text-red-700"
                  title="Clear collection"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Indexing Notification */}
      {indexingNotification && (
        <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-2 rounded-lg text-sm flex justify-between items-center">
          <span>{indexingNotification}</span>
          <button onClick={() => setIndexingNotification(null)} className="text-green-600 hover:text-green-800">
            <X size={16} />
          </button>
        </div>
      )}

      <div className="flex-1 bg-white border border-slate-200 rounded-xl shadow-sm flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
          {chatHistory.length === 0 && (
            <div className="text-center text-slate-400 mt-20">
              <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
              <p className="font-medium mb-2">Ask questions like:</p>
              <ul className="mt-4 space-y-2 text-sm text-left max-w-md mx-auto">
                {queryMode === 'all-database' && (
                  <>
                    <li className="bg-white border border-slate-200 p-2 rounded">"Who are the top A-grade candidates?"</li>
                    <li className="bg-white border border-slate-200 p-2 rounded">"Which candidates have Python and React experience?"</li>
                    <li className="bg-white border border-slate-200 p-2 rounded">"Compare all candidates with cloud certifications."</li>
                  </>
                )}
                {queryMode === 'all-job' && (
                  <>
                    <li className="bg-white border border-slate-200 p-2 rounded">"Who has the most experience with React for this job?"</li>
                    <li className="bg-white border border-slate-200 p-2 rounded">"Summarize the strengths of all candidates."</li>
                    <li className="bg-white border border-slate-200 p-2 rounded">"Compare the top 3 candidates for this position."</li>
                  </>
                )}
                {selectedCandidateId && (
                  <>
                    <li className="bg-white border border-slate-200 p-2 rounded">"Does this candidate have any cloud certifications?"</li>
                    <li className="bg-white border border-slate-200 p-2 rounded">"What projects has this candidate worked on?"</li>
                    <li className="bg-white border border-slate-200 p-2 rounded">"Summarize their leadership experience."</li>
                  </>
                )}
              </ul>
            </div>
          )}
          {chatHistory.map(msg => {
            // Format message text for better display
            const formatMessage = (text: string) => {
              // Helper to parse inline markdown
              const parseInlineMarkdown = (line: string) => {
                const parts: React.ReactNode[] = [];
                let lastIndex = 0;
                const boldRegex = /\*\*([^*]+)\*\*/g;
                let match;
                while ((match = boldRegex.exec(line)) !== null) {
                  if (match.index > lastIndex) {
                    parts.push(line.substring(lastIndex, match.index));
                  }
                  parts.push(<strong key={match.index}>{match[1]}</strong>);
                  lastIndex = match.index + match[0].length;
                }
                if (lastIndex < line.length) {
                  parts.push(line.substring(lastIndex));
                }
                return parts.length > 0 ? parts : line;
              };
              // Split by lines
              const lines = text.split('\n');
              return lines.map((line, idx) => {
                // Check if line starts with bullet point or number
                const bulletMatch = line.match(/^[\s-]*[\*\-•]\s+(.+)/);
                const numberMatch = line.match(/^\s*(\d+)[\.)\s]+(.+)/);

                if (bulletMatch) {
                  return (
                    <div key={idx} className="flex items-start gap-2 mb-1">
                      <span className="text-blue-600 mt-1 flex-shrink-0">•</span>
                      <span className="flex-1">{parseInlineMarkdown(bulletMatch[1])}</span>
                    </div>
                  );
                } else if (numberMatch) {
                  return (
                    <div key={idx} className="flex items-start gap-2 mb-1">
                      <span className="font-semibold text-blue-600 flex-shrink-0">{numberMatch[1]}.</span>
                      <span className="flex-1">{parseInlineMarkdown(numberMatch[2])}</span>
                    </div>
                  );
                } else if (line.trim()) {
                  return <p key={idx} className="mb-2">{parseInlineMarkdown(line)}</p>;
                }
                return null;
              });
            };

            return (
              <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-2xl p-4 ${msg.sender === 'user' ? 'bg-recruiter-600 text-white rounded-br-none' : 'bg-white border border-slate-200 text-slate-700 rounded-bl-none shadow-sm'}`}>
                  <div className="text-sm leading-relaxed">
                    {msg.sender === 'ai' ? formatMessage(msg.text) : <p>{msg.text}</p>}
                  </div>

                  {/* New source display - only document names */}
                  {msg.source_metadata && msg.source_metadata.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-100">
                      <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-2">Sources:</p>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.source_metadata.map((source, idx) => (
                          <span
                            key={idx}
                            className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-medium ${source.type === 'cv'
                              ? 'bg-blue-50 text-blue-700 border border-blue-200'
                              : 'bg-purple-50 text-purple-700 border border-purple-200'
                              }`}
                          >
                            {source.type === 'cv' ? '📄' : '💼'} {source.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <span className="text-[10px] opacity-60 block mt-2 text-right">
                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            );
          })}
          {isChatLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-none p-4 shadow-sm w-3/4">
                <div className="flex items-center space-x-2 mb-3">
                  <div className="w-2 h-2 bg-recruiter-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-recruiter-400 rounded-full animate-bounce delay-75"></div>
                  <div className="w-2 h-2 bg-recruiter-400 rounded-full animate-bounce delay-150"></div>
                </div>
                <div className="space-y-2">
                  <div className="h-2 bg-slate-100 rounded animate-pulse w-full"></div>
                  <div className="h-2 bg-slate-100 rounded animate-pulse w-5/6"></div>
                  <div className="h-2 bg-slate-100 rounded animate-pulse w-4/6"></div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="p-4 bg-white border-t border-slate-200">
          <div className="flex space-x-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
              placeholder="Ask a question about the candidates..."
              className="flex-1 border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-recruiter-500 focus:border-recruiter-500 outline-none"
            />
            <button
              onClick={handleAskQuestion}
              disabled={!chatInput.trim() || isChatLoading}
              className="bg-recruiter-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-recruiter-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCandidatesList = () => {
    const handleDeleteCandidate = async (candidateId: string, candidateName: string) => {
      if (!confirm(`Are you sure you want to delete ${candidateName}?`)) {
        return;
      }

      try {
        setDbLoading(true);
        await deleteCandidate(candidateId);
        await fetchAllCandidates();
        alert(`${candidateName} deleted successfully!`);
      } catch (err) {
        console.error('Failed to delete candidate:', err);
        alert('Failed to delete candidate');
      } finally {
        setDbLoading(false);
      }
    };

    return (
      <div className="max-w-7xl mx-auto py-8 px-4">
        <div className="mb-6 flex justify-between items-end">
          <div>
            <h2 className="text-2xl font-bold text-slate-800">All Candidates Database</h2>
            <p className="text-slate-500">View and manage all uploaded candidates</p>
          </div>
          <button
            onClick={() => {
              setQueryMode('all-database');
              setSelectedCandidateId(null);
              setActiveTab('rag');
            }}
            className="flex items-center px-4 py-2 bg-recruiter-600 hover:bg-recruiter-700 text-white rounded-lg font-medium shadow-md transition-all"
          >
            <MessageSquare size={18} className="mr-2" />
            Ask AI About All Candidates
          </button>
        </div>

        {dbLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 text-recruiter-600 animate-spin" />
          </div>
        ) : allCandidates.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
            <User size={48} className="mx-auto text-slate-300 mb-4" />
            <h3 className="text-lg font-semibold text-slate-700 mb-2">No Candidates Yet</h3>
            <p className="text-slate-500">Upload CVs in the "Upload Docs" tab to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {allCandidates.map((candidate) => (
              <div key={candidate.id} className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-all">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mr-3">
                      <User size={24} className="text-slate-400" />
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-900">{candidate.name}</h3>
                      <p className="text-xs text-slate-500">{candidate.email}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteCandidate(candidate.id, candidate.name)}
                    className="text-slate-400 hover:text-red-600 transition-colors"
                    title="Delete candidate"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>

                <div className="mb-4">
                  <p className="text-sm text-slate-600 mb-4">{candidate.summary}</p>

                  {/* Job Title */}
                  {candidate.jobTitle && (
                    <div className="flex items-center justify-between mb-1">
                      <div className="text-xs text-slate-500 mb-1">Matched for</div>
                      <div className="text-sm font-semibold text-slate-700 text-blue-600">{candidate.jobTitle}</div>
                    </div>
                  )}

                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-slate-800">{candidate.matchScore}%</span>
                    <span className={`px-2 py-1 rounded text-xs font-bold ${candidate.matchScore >= 85 ? 'bg-green-100 text-green-700' : candidate.matchScore >= 75 ? 'bg-yellow-100 text-yellow-800' : 'bg-slate-100 text-slate-700'}`}>
                      Grade {candidate.grade}
                    </span>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="text-xs text-slate-500 mb-1">Skills</div>
                  <div className="flex flex-wrap gap-1">
                    {(candidate.allSkills && candidate.allSkills.length > 0 ? candidate.allSkills : candidate.matchedSkills).slice(0, 5).map(skill => (
                      <span key={skill} className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded border border-blue-100">
                        {skill}
                      </span>
                    ))}
                    {((candidate.allSkills && candidate.allSkills.length > 0 ? candidate.allSkills : candidate.matchedSkills).length > 5) && (
                      <span className="text-xs text-slate-400 self-center">
                        +{(candidate.allSkills && candidate.allSkills.length > 0 ? candidate.allSkills : candidate.matchedSkills).length - 5}
                      </span>
                    )}
                  </div>
                </div>

                <div className="text-xs text-slate-400 mb-3">
                  {candidate.experienceYears} years experience
                </div>

                <button
                  onClick={() => {
                    setSelectedCandidateId(candidate.id);
                    setCandidates(prev => {
                      const exists = prev.find(c => c.id === candidate.id);
                      if (!exists) {
                        return [...prev, candidate];
                      }
                      return prev;
                    });
                    setActiveTab('results');
                  }}
                  className="w-full bg-recruiter-600 hover:bg-recruiter-700 text-white text-sm font-medium py-2 rounded-lg transition-colors"
                >
                  View Details
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-50 pl-64">
      {renderSidebar()}
      <div className="h-full">
        {activeTab === 'upload' && renderUpload()}
        {activeTab === 'results' && renderResults()}
        {activeTab === 'analytics' && renderAnalytics()}
        {activeTab === 'rag' && renderRAG()}
        {activeTab === 'candidates' && renderCandidatesList()}
      </div>
      {renderComparisonModal()}
    </div>
  );
};