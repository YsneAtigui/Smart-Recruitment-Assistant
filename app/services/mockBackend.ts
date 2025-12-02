import { Candidate, JobDescription, Skill } from '../types';

// Helper to generate random delays
export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const NAMES = ["John Doe", "Jane Smith", "Alex Johnson", "Sarah Williams", "Michael Chen", "Emily Davis"];
const ROLES = ["Senior Frontend Engineer", "Full Stack Developer", "DevOps Engineer", "Data Scientist"];

export const mockParseJD = async (file: File): Promise<JobDescription> => {
  await delay(1500); // Simulate processing
  return {
    title: "Senior React Engineer",
    company: "TechNova Inc.",
    requiredSkills: ["React", "TypeScript", "Tailwind CSS", "Node.js", "AWS", "GraphQL"],
    minExperience: 5,
    rawText: "Sample JD content..."
  };
};

export const mockParseCV = async (file: File): Promise<Candidate> => {
  // Return a dummy candidate based on the filename or random
  const name = NAMES[Math.floor(Math.random() * NAMES.length)];
  const score = 65 + Math.floor(Math.random() * 30); // 65-95
  
  let grade: Candidate['grade'] = 'C';
  if (score >= 90) grade = 'A+';
  else if (score >= 85) grade = 'A';
  else if (score >= 75) grade = 'B';
  
  const matched = ["React", "TypeScript", "Node.js"];
  const missing = ["AWS", "GraphQL", "Kubernetes"];

  return {
    id: Math.random().toString(36).substr(2, 9),
    name,
    email: `${name.toLowerCase().replace(' ', '.')}@example.com`,
    role: ROLES[Math.floor(Math.random() * ROLES.length)],
    matchScore: score,
    grade,
    experienceYears: 3 + Math.floor(Math.random() * 7),
    scores: {
      semantic: score - 5 + Math.floor(Math.random() * 10),
      skills: score,
      experience: score - 10 + Math.floor(Math.random() * 15),
      education: 85,
    },
    matchedSkills: matched,
    missingSkills: missing,
    strengths: [
      "Strong proficiency in Frontend Technologies",
      "Demonstrated leadership in agile environments",
      "Consistent track record of delivery"
    ],
    weaknesses: [
      "Lack of cloud infrastructure experience",
      "Limited exposure to container orchestration"
    ],
    recommendations: [
      "Obtain AWS Cloud Practitioner certification",
      "Build a side project using GraphQL",
      "Contribute to open source Kubernetes tools"
    ],
    summary: `${name} is a strong candidate with solid experience in modern web development. While they excel in UI implementation, they could benefit from deeper backend and infrastructure knowledge.`
  };
};

export const mockRAGQuery = async (query: string, candidateName: string): Promise<string> => {
  await delay(2000);
  return `Based on ${candidateName}'s CV, they have extensive experience with React and TypeScript. Regarding "${query}", the document mentions a project delivered in 2023 that reduced load times by 40%.`;
};
