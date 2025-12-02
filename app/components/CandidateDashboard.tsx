import React, { useState } from 'react';
import { FileUpload } from './ui/FileUpload';
import { ArrowLeft, CheckCircle, AlertTriangle, TrendingUp, Download, Star, BookOpen, Target } from './ui/Icons';
import { parseCV, parseJD, matchCVtoJD } from '../services/apiBackend';
import { Candidate, JobDescription } from '../types';

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

  const handleAnalyze = async (files: File[], type: 'cv' | 'jd') => {
    setError(null);
    try {
      if (type === 'cv') {
        // Just parse and store raw data, we'll match later
        const data = await parseCV(files[0]);
        setCvRawData(data);
        // Create a temporary candidate object for UI feedback
        setCvFile({ name: files[0].name } as any);
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
      setCvFile(matchResult);
      setStep('analysis');
    } catch (err) {
      console.error("Analysis error:", err);
      setError("Failed to analyze match. Please try again.");
    } finally {
      setIsAnalyzing(false);
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

        {/* Score Hero */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 mb-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-32 bg-candidate-50 rounded-full blur-3xl opacity-50 -mr-16 -mt-16"></div>

          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between">
            <div className="mb-6 md:mb-0">
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-candidate-100 text-candidate-700 text-sm font-bold mb-4">
                Match Grade: {cvFile.grade}
              </div>
              <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-2">
                You are a <span className="text-candidate-600">Great Match!</span>
              </h2>
              <p className="text-slate-600 max-w-lg text-lg">
                Your profile aligns well with the core requirements of this role.
                Focus on the few missing skills to become a top-tier candidate.
              </p>
            </div>

            <div className="relative h-40 w-40 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="80" cy="80" r="70" stroke="#e2e8f0" strokeWidth="12" fill="none" />
                <circle cx="80" cy="80" r="70" stroke="#10b981" strokeWidth="12" fill="none" strokeDasharray="440" strokeDashoffset={440 - (440 * cvFile.matchScore) / 100} strokeLinecap="round" className="transition-all duration-1000 ease-out" />
              </svg>
              <div className="absolute text-center">
                <span className="text-4xl font-extrabold text-slate-900 block">{cvFile.matchScore}%</span>
                <span className="text-xs text-slate-500 font-bold uppercase">Fit Score</span>
              </div>
            </div>
          </div>
        </div>

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
      </main>
    </div>
  );
};