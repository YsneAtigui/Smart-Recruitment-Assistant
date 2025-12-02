import React, { useState } from 'react';
import { Role } from './types';
import { LandingPage } from './components/LandingPage';
import { RecruiterDashboard } from './components/RecruiterDashboard';
import { CandidateDashboard } from './components/CandidateDashboard';

const App: React.FC = () => {
  const [currentRole, setCurrentRole] = useState<Role>(null);

  const renderView = () => {
    switch (currentRole) {
      case 'recruiter':
        return <RecruiterDashboard onBack={() => setCurrentRole(null)} />;
      case 'candidate':
        return <CandidateDashboard onBack={() => setCurrentRole(null)} />;
      default:
        return <LandingPage onRoleSelect={setCurrentRole} />;
    }
  };

  return (
    <div className="font-sans text-slate-900 bg-slate-50 min-h-screen">
      {renderView()}
    </div>
  );
};

export default App;