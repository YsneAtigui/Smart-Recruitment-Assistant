import React from 'react';
import { Briefcase, User, CheckCircle, ArrowLeft } from './ui/Icons';
import { Role } from '../types';

interface LandingPageProps {
  onRoleSelect: (role: Role) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onRoleSelect }) => {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Hero Header */}
      <header className="py-16 text-center px-4">
        <div className="inline-flex items-center justify-center p-3 bg-white rounded-xl shadow-md mb-6">
          <div className="h-8 w-8 bg-gradient-to-tr from-blue-600 to-emerald-500 rounded-lg mr-3"></div>
          <span className="text-xl font-bold text-slate-800 tracking-tight">SmartRecruit AI</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 mb-4 tracking-tight">
          Intelligent Recruitment, <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-emerald-500">Simplified.</span>
        </h1>
        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
          Leverage AI to match the perfect candidates with the right roles. 
          Advanced parsing, semantic matching, and skill gap analysis for modern hiring.
        </p>
      </header>

      {/* Role Selection */}
      <main className="flex-grow flex items-center justify-center px-4 pb-20">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl w-full">
          
          {/* Recruiter Card */}
          <div 
            onClick={() => onRoleSelect('recruiter')}
            className="group relative bg-white rounded-2xl p-8 shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-200 hover:border-recruiter-500 cursor-pointer overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <Briefcase size={120} className="text-recruiter-600" />
            </div>
            
            <div className="relative z-10">
              <div className="h-14 w-14 bg-recruiter-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-recruiter-500 transition-colors duration-300">
                <Briefcase size={28} className="text-recruiter-600 group-hover:text-white transition-colors" />
              </div>
              
              <h2 className="text-2xl font-bold text-slate-900 mb-2">I'm a Recruiter</h2>
              <p className="text-slate-600 mb-6">Find the best talent for your open positions with AI-powered matching.</p>
              
              <ul className="space-y-3 mb-8">
                {[
                  "Batch upload CVs & extract data",
                  "AI-powered semantic matching",
                  "Deep skill gap analysis",
                  "Ask questions about candidates"
                ].map((item, i) => (
                  <li key={i} className="flex items-center text-slate-700 text-sm">
                    <CheckCircle size={16} className="text-recruiter-500 mr-2" />
                    {item}
                  </li>
                ))}
              </ul>

              <button className="w-full py-3 px-6 rounded-lg bg-white border-2 border-recruiter-600 text-recruiter-600 font-semibold group-hover:bg-recruiter-600 group-hover:text-white transition-all">
                Start Recruiting
              </button>
            </div>
          </div>

          {/* Candidate Card */}
          <div 
            onClick={() => onRoleSelect('candidate')}
            className="group relative bg-white rounded-2xl p-8 shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-200 hover:border-candidate-500 cursor-pointer overflow-hidden"
          >
             <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
              <User size={120} className="text-candidate-600" />
            </div>

            <div className="relative z-10">
              <div className="h-14 w-14 bg-candidate-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-candidate-500 transition-colors duration-300">
                <User size={28} className="text-candidate-600 group-hover:text-white transition-colors" />
              </div>
              
              <h2 className="text-2xl font-bold text-slate-900 mb-2">I'm a Candidate</h2>
              <p className="text-slate-600 mb-6">Discover your perfect job fit and get personalized career advice.</p>
              
              <ul className="space-y-3 mb-8">
                {[
                  "Get an instant suitability score",
                  "Identify missing critical skills",
                  "Receive CV improvement tips",
                  "Personalized action plan"
                ].map((item, i) => (
                  <li key={i} className="flex items-center text-slate-700 text-sm">
                    <CheckCircle size={16} className="text-candidate-500 mr-2" />
                    {item}
                  </li>
                ))}
              </ul>

              <button className="w-full py-3 px-6 rounded-lg bg-white border-2 border-candidate-600 text-candidate-600 font-semibold group-hover:bg-candidate-600 group-hover:text-white transition-all">
                Check My Fit
              </button>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
};