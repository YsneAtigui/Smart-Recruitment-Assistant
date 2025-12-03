import React, { useState } from 'react';
import { FileUpload } from './ui/FileUpload';
import { ArrowLeft, CheckCircle, AlertTriangle, TrendingUp, Download, Star, BookOpen, Target, Briefcase, Building2, Calendar, GraduationCap, MessageCircle, Send, Loader2 } from './ui/Icons';
import { parseCV, parseJD, matchCVtoJD, summarizeCV, indexCVforRAG, queryRAG } from '../services/apiBackend';
import { Candidate, JobDescription, ChatMessage } from '../types';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

interface CandidateDashboardProps {
  onBack: () => void;
}

export const CandidateDashboard: React.FC<CandidateDashboardProps> = ({ onBack }) => {
  const [step, setStep] = useState<'upload' | 'analysis'>('upload');
  const [cvFile, setCvFile] = useState<Candidate | null>(null);
  const [cvRawData, setCvRawData] = useState<any>(null);
  const [jdFile, setJdFile] = useState<JobDescription | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // New State for enhancements
  const [activeTab, setActiveTab] = useState<'overview' | 'experience' | 'assistant'>('overview');
  const [cvSummary, setCvSummary] = useState<string>("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);

  const handleAnalyze = async (files: File[], type: 'cv' | 'jd') => {
    setError(null);
    try {
      if (type === 'cv') {
        // Just parse and store raw data, we'll match later
        const data = await parseCV(files[0]);
        setCvRawData(data);
        // Create a temporary candidate object for UI feedback
        setCvFile({
          id: data.candidate_id || files[0].name,
          name: files[0].name
        } as any);
      } else {
        const data = await parseJD(files[0]);
        setJdFile(data);
      }
    } catch (err) {
      console.error("Upload error:", err);
      setError("Failed to process file. Please try again.");
    }
  };

  const runAnalysis = async () => {
    if (!cvRawData || !jdFile) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const matchResult = await matchCVtoJD(cvRawData, jdFile);
      // Ensure we keep the original candidate ID if the match result generates a new one that doesn't match our RAG index
      if (cvRawData.candidate_id) {
        matchResult.id = cvRawData.candidate_id;
      }
      setCvFile(matchResult);
      setStep('analysis');
    } catch (err) {
      console.error("Analysis error:", err);
      setError("Failed to analyze match. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Initialize AI features after successful match
  React.useEffect(() => {
    if (step === 'analysis' && cvFile && cvFile.id) {
      // 1. Generate Summary
      if (cvFile.rawText) {
        summarizeCV(cvFile.rawText).then(summary => setCvSummary(summary)).catch(console.error);
      }

      // 2. Index for RAG
      if (cvFile.rawText && !isIndexing) {
        setIsIndexing(true);
        indexCVforRAG(cvFile.id, cvFile.name, cvFile.rawText, jdFile?.id)
          .then(() => {
            console.log("CV Indexed for RAG");
            // Add initial welcome message
            setChatMessages([{
              id: 'welcome',
              sender: 'ai',
              text: `Hello ${cvFile.name.split(' ')[0]}! I've analyzed your profile against this job description. Ask me anything about how to improve your chances!`,
              timestamp: new Date()
            }]);
          })
          .catch(console.error)
          .finally(() => setIsIndexing(false));
      }
    }
  }, [step, cvFile]);

  const handleSendMessage = async () => {
    if (!chatInput.trim() || !cvFile) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: chatInput,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMsg]);
    setChatInput("");
    setIsChatLoading(true);

    try {
      const { answer, sources, source_metadata } = await queryRAG(
        cvFile.id,
        cvFile.name,
        userMsg.text,
        'candidate',
        jdFile?.id  // Pass job ID for context
      );

      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: answer,
        sources: sources,
        source_metadata: source_metadata as any,  // Type compatibility fix
        timestamp: new Date()
      };

      setChatMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setIsChatLoading(false);
    }
  };

  if (step === 'upload') {
    return (
      <div className="min-h-screen bg-slate-50 py-12 px-4">
        <div className="max-w-3xl mx-auto">
          <button onClick={onBack} className="mb-8 flex items-center text-slate-500 hover:text-slate-900 font-medium transition-colors">
            <ArrowLeft size={20} className="mr-2" /> Back to Home
          </button>

          <div className="text-center mb-10">
            <h1 className="text-3xl font-extrabold text-slate-900 mb-2">Check Your Job Fit</h1>
            <p className="text-slate-600">Upload your CV and the job description to get an instant AI analysis.</p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center justify-center">
              <AlertTriangle className="mr-2" size={20} />
              {error}
            </div>
          )}

          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-8 border-b border-slate-100">
              <h2 className="text-lg font-bold text-slate-800 mb-4">1. Upload Your CV</h2>
              {cvFile ? (
                <div className="flex items-center p-4 bg-candidate-50 border border-candidate-200 rounded-lg">
                  <CheckCircle className="text-candidate-500 mr-3" />
                  <div>
                    <p className="font-medium text-candidate-900">CV Uploaded Successfully</p>
                    <p className="text-xs text-candidate-700">{cvFile.name}</p>
                  </div>
                </div>
              ) : (
                <FileUpload label="" color="green" onFilesSelected={(f) => handleAnalyze(f, 'cv')} />
              )}
            </div>

            <div className="p-8">
              <h2 className="text-lg font-bold text-slate-800 mb-4">2. Upload Job Description</h2>
              {jdFile ? (
                <div className="flex items-center p-4 bg-candidate-50 border border-candidate-200 rounded-lg">
                  <CheckCircle className="text-candidate-500 mr-3" />
                  <div>
                    <p className="font-medium text-candidate-900">JD Uploaded Successfully</p>
                    <p className="text-xs text-candidate-700">{jdFile.title}</p>
                  </div>
                </div>
              ) : (
                <FileUpload label="" color="green" onFilesSelected={(f) => handleAnalyze(f, 'jd')} />
              )}
            </div>

            <div className="p-6 bg-slate-50 border-t border-slate-200 flex justify-end">
              <button
                onClick={runAnalysis}
                disabled={!cvFile || !jdFile || isAnalyzing}
                className={`px-8 py-3 rounded-lg font-bold text-white shadow-md transition-all ${!cvFile || !jdFile ? 'bg-slate-300 cursor-not-allowed' : 'bg-candidate-600 hover:bg-candidate-700 hover:shadow-lg'
                  }`}
              >
                {isAnalyzing ? "Analyzing Match..." : "Analyze My Fit"}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Analysis View
  if (!cvFile || !jdFile) return null;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <button onClick={() => setStep('upload')} className="mr-4 text-slate-400 hover:text-slate-800">
              <ArrowLeft size={24} />
            </button>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Fit Analysis Result</h1>
              <p className="text-xs text-slate-500">{jdFile.title} @ {jdFile.company}</p>
            </div>
          </div>
          <button className="flex items-center text-sm font-medium text-candidate-600 border border-candidate-200 px-3 py-1.5 rounded-lg hover:bg-candidate-50">
            <Download size={16} className="mr-2" /> Export Report
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">

        {/* Score Hero with Radar Chart */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 mb-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-32 bg-candidate-50 rounded-full blur-3xl opacity-50 -mr-16 -mt-16"></div>

          <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
            <div className="md:col-span-2">
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-candidate-100 text-candidate-700 text-sm font-bold mb-4">
                Match Grade: {cvFile.grade}
              </div>
              <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-2">
                You are a <span className="text-candidate-600">Great Match!</span>
              </h2>
              <p className="text-slate-600 text-lg mb-6">
                Your profile aligns well with the core requirements of this role.
                Focus on the few missing skills to become a top-tier candidate.
              </p>

              {/* Tabs Navigation */}
              <div className="flex space-x-1 bg-slate-100 p-1 rounded-lg inline-flex">
                <button
                  onClick={() => setActiveTab('overview')}
                  className={`px-4 py-2 rounded-md text-sm font-bold transition-all ${activeTab === 'overview' ? 'bg-white text-candidate-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    }`}
                >
                  Overview
                </button>
                <button
                  onClick={() => setActiveTab('experience')}
                  className={`px-4 py-2 rounded-md text-sm font-bold transition-all ${activeTab === 'experience' ? 'bg-white text-candidate-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    }`}
                >
                  Experience & Education
                </button>
                <button
                  onClick={() => setActiveTab('assistant')}
                  className={`px-4 py-2 rounded-md text-sm font-bold transition-all ${activeTab === 'assistant' ? 'bg-white text-candidate-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    }`}
                >
                  AI Assistant
                </button>
              </div>
            </div>

            <div className="flex flex-col items-center justify-center">
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={[
                    { subject: 'Semantic', A: cvFile.scores.semantic, fullMark: 100 },
                    { subject: 'Skills', A: cvFile.scores.skills, fullMark: 100 },
                    { subject: 'Experience', A: cvFile.scores.experience, fullMark: 100 },
                    { subject: 'Education', A: cvFile.scores.education, fullMark: 100 },
                  ]}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
                    <Radar
                      name="My Score"
                      dataKey="A"
                      stroke="#059669"
                      fill="#10b981"
                      fillOpacity={0.6}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
              <div className="text-center -mt-4">
                <span className="text-3xl font-extrabold text-slate-900">{cvFile.matchScore}%</span>
                <span className="text-xs text-slate-500 font-bold uppercase block">Overall Fit</span>
              </div>
            </div>
          </div>
        </div>

        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left: Skill Gap */}
            <div className="lg:col-span-2 space-y-8">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center">
                  <Target className="mr-2 text-candidate-500" /> Skill Analysis
                </h3>

                <div className="space-y-6">
                  <div>
                    <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">✅ Skills You Have</h4>
                    <div className="flex flex-wrap gap-2">
                      {cvFile.matchedSkills.map(skill => (
                        <span key={skill} className="px-3 py-1.5 bg-candidate-50 text-candidate-700 border border-candidate-100 rounded-lg text-sm font-medium flex items-center">
                          <CheckCircle size={14} className="mr-1.5" /> {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">⚠️ Skills To Improve</h4>
                    <div className="flex flex-wrap gap-2">
                      {cvFile.missingSkills.map(skill => (
                        <span key={skill} className="px-3 py-1.5 bg-amber-50 text-amber-700 border border-amber-100 rounded-lg text-sm font-medium flex items-center">
                          <AlertTriangle size={14} className="mr-1.5" /> {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center">
                  <TrendingUp className="mr-2 text-blue-500" /> Actionable Recommendations
                </h3>
                <div className="space-y-4">
                  {cvFile.recommendations.map((rec, i) => (
                    <div key={i} className="flex p-4 bg-slate-50 rounded-xl border border-slate-100 transition-hover hover:border-blue-200 hover:shadow-sm">
                      <div className="h-8 w-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold mr-4 flex-shrink-0">
                        {i + 1}
                      </div>
                      <div>
                        <p className="text-slate-800 font-medium">{rec}</p>
                        <p className="text-sm text-slate-500 mt-1">Suggested timeline: 2-4 weeks</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right: Insights */}
            <div className="space-y-6">
              <div className="bg-gradient-to-br from-candidate-600 to-emerald-600 rounded-xl shadow-lg p-6 text-white">
                <h3 className="font-bold text-lg mb-2 flex items-center"><Star className="mr-2" fill="currentColor" /> Quick Wins</h3>
                <p className="text-candidate-100 text-sm mb-4">Focus on these areas to boost your score immediately:</p>
                <ul className="space-y-3">
                  <li className="flex items-start text-sm">
                    <div className="bg-white/20 p-1 rounded mr-3 mt-0.5"><CheckCircle size={12} /></div>
                    Add certification in {cvFile.missingSkills[0] || "Cloud"}
                  </li>
                  <li className="flex items-start text-sm">
                    <div className="bg-white/20 p-1 rounded mr-3 mt-0.5"><CheckCircle size={12} /></div>
                    Highlight leadership in your summary
                  </li>
                </ul>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="font-bold text-slate-900 mb-4 flex items-center"><BookOpen className="mr-2 text-slate-400" /> Resources</h3>
                <div className="space-y-3">
                  {cvFile.missingSkills.map((skill, i) => (
                    <a key={i} href="#" className="block p-3 rounded-lg border border-slate-200 hover:border-candidate-300 hover:bg-candidate-50 transition-all">
                      <p className="text-sm font-bold text-slate-800">Learn {skill}</p>
                      <p className="text-xs text-slate-500 mt-1">Coursera • 12 Hours</p>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'experience' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              {/* Experience Section */}
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center">
                  <Briefcase className="mr-2 text-candidate-500" /> Professional Experience
                </h3>
                <div className="space-y-6">
                  {cvFile.experience && cvFile.experience.length > 0 ? (
                    cvFile.experience.map((exp, i) => (
                      <div key={i} className="flex gap-4 p-4 bg-slate-50 rounded-lg border border-slate-100">
                        <div className="mt-1">
                          <div className="h-10 w-10 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-400 shadow-sm">
                            <Building2 size={20} />
                          </div>
                        </div>
                        <div>
                          <h4 className="font-bold text-slate-900 text-lg">{exp}</h4>
                          <p className="text-slate-500 text-sm flex items-center mt-1">
                            <Calendar size={14} className="mr-1" /> Detected from CV
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500 italic">No experience details detected.</p>
                  )}
                </div>
              </div>

              {/* Education Section */}
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="text-lg font-bold text-slate-900 mb-6 flex items-center">
                  <GraduationCap className="mr-2 text-blue-500" /> Education
                </h3>
                <div className="space-y-6">
                  {cvFile.education && cvFile.education.length > 0 ? (
                    cvFile.education.map((edu, i) => (
                      <div key={i} className="flex gap-4 p-4 bg-slate-50 rounded-lg border border-slate-100">
                        <div className="mt-1">
                          <div className="h-10 w-10 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-400 shadow-sm">
                            <BookOpen size={20} />
                          </div>
                        </div>
                        <div>
                          <h4 className="font-bold text-slate-900 text-lg">{edu}</h4>
                          <p className="text-slate-500 text-sm flex items-center mt-1">
                            <CheckCircle size={14} className="mr-1 text-green-500" /> Verified Education
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-500 italic">No education details detected.</p>
                  )}
                </div>
              </div>
            </div>

            {/* Right Sidebar for Experience */}
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="font-bold text-slate-900 mb-4">Career Summary</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                    <span className="text-slate-600 text-sm">Total Experience</span>
                    <span className="font-bold text-slate-900">{cvFile.experienceYears} Years</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
                    <span className="text-slate-600 text-sm">Education Level</span>
                    <span className="font-bold text-slate-900">{cvFile.education ? 'Detected' : 'Unknown'}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'assistant' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Chat Interface */}
            <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col h-[600px]">
              <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50 rounded-t-xl">
                <h3 className="font-bold text-slate-800 flex items-center">
                  <MessageCircle className="mr-2 text-candidate-600" /> AI Career Coach
                </h3>
                <span className="text-xs font-medium px-2 py-1 bg-green-100 text-green-700 rounded-full flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></span> Online
                </span>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {chatMessages.map((msg) => {
                  // Format message text with markdown support
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
                            <span className="text-candidate-600 mt-1 flex-shrink-0">•</span>
                            <span className="flex-1">{parseInlineMarkdown(bulletMatch[1])}</span>
                          </div>
                        );
                      } else if (numberMatch) {
                        return (
                          <div key={idx} className="flex items-start gap-2 mb-1">
                            <span className="font-semibold text-candidate-600 flex-shrink-0">{numberMatch[1]}.</span>
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
                      <div className={`max-w-[80%] p-4 rounded-2xl ${msg.sender === 'user'
                        ? 'bg-candidate-600 text-white rounded-br-none'
                        : 'bg-white border border-slate-200 text-slate-700 rounded-bl-none shadow-sm'
                        }`}>
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
                                    ? 'bg-green-50 text-green-700 border border-green-200'
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
                    <div className="bg-slate-100 p-3 rounded-2xl rounded-bl-none flex items-center space-x-2">
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                )}
              </div>

              <div className="p-4 border-t border-slate-100">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask about your skills, resume, or the job..."
                    className="flex-1 border border-slate-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-candidate-500 focus:border-transparent"
                    disabled={isChatLoading}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!chatInput.trim() || isChatLoading}
                    className="bg-candidate-600 text-white p-2 rounded-lg hover:bg-candidate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <Send size={20} />
                  </button>
                </div>
              </div>
            </div>

            {/* AI Summary Sidebar */}
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 className="font-bold text-slate-900 mb-4 flex items-center">
                  <Star className="mr-2 text-yellow-500" /> AI Profile Summary
                </h3>
                <div className="prose prose-sm text-slate-600">
                  {cvSummary ? (
                    <p className="text-sm leading-relaxed">{cvSummary}</p>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-8 text-slate-400">
                      <Loader2 className="animate-spin mb-2" />
                      <span className="text-xs">Generating summary...</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
                <h4 className="font-bold text-blue-800 mb-2 text-sm">Suggested Questions</h4>
                <ul className="space-y-2">
                  {[
                    "What are my top 3 strengths?",
                    "How can I improve my resume?",
                    "What skills am I missing?",
                    "Is my experience relevant?"
                  ].map((q, i) => (
                    <li
                      key={i}
                      onClick={() => setChatInput(q)}
                      className="text-xs text-blue-600 bg-white p-2 rounded border border-blue-200 cursor-pointer hover:bg-blue-50 transition-colors"
                    >
                      {q}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};