"""
Shared pytest fixtures for Smart Recruitment Assistant tests.
"""
import pytest
import numpy as np
from src.models import CV, JobDescription, MatchResult


@pytest.fixture
def sample_cv_text():
    """Sample CV text for testing."""
    return """John Doe
Software Engineer

Contact:
Email: john.doe@example.com
Phone: +1-555-0123

EXPERIENCE
Senior Software Engineer at Tech Corp (2020 - 2023) - 3 years
- Led development of microservices architecture
- Implemented CI/CD pipelines using Docker and Kubernetes
- Mentored junior developers

Software Developer at StartupXYZ (2018 - 2020) - 2 years
- Developed full-stack web applications
- Worked with React, Node.js, and PostgreSQL

EDUCATION
Master of Science in Computer Science
Stanford University (2016-2018)

Bachelor of Science in Computer Science  
UC Berkeley (2012-2016)

SKILLS
Python, JavaScript, TypeScript, Java
React, Node.js, Django, Flask
PostgreSQL, MongoDB, Redis
Docker, Kubernetes, AWS
Machine Learning, NLP
Git, CI/CD, Agile
"""


@pytest.fixture
def sample_jd_text():
    """Sample job description text for testing."""
    return """Senior Full-Stack Developer

Company: InnovateTech Solutions
Location: San Francisco, CA (Hybrid)
Type: Full-time

ABOUT THE ROLE
We're looking for an experienced full-stack developer to join our growing team.

RESPONSIBILITIES
- Design and implement scalable web applications
- Work with React and Node.js
- Develop RESTful APIs
- Collaborate with cross-functional teams
- Participate in code reviews

REQUIREMENTS
Experience: 4-6 years of professional software development
Education: Bachelor's degree in Computer Science or related field

REQUIRED SKILLS
- JavaScript/TypeScript
- React.js
- Node.js
- PostgreSQL or similar SQL database
- Git version control
- RESTful API design

PREFERRED SKILLS
- Python
- Docker
- AWS or cloud platforms
- CI/CD pipelines
- Agile methodologies
"""


@pytest.fixture
def sample_cv_data():
    """Sample structured CV data (as returned by extraction)."""
    return {
        "name": "John Doe",
        "contact": {
            "email": "john.doe@example.com",
            "phone": "+1-555-0123"
        },
        "skills": ["Python", "JavaScript", "React", "Node.js", "Docker", "Kubernetes", "AWS"],
        "experience": [
            "Senior Software Engineer at Tech Corp (2020-2023) - 3 years",
            "Software Developer at StartupXYZ (2018-2020) - 2 years"
        ],
        "education": [
            "Master of Science in Computer Science, Stanford University (2016-2018)",
            "Bachelor of Science in Computer Science, UC Berkeley (2012-2016)"
        ],
        "diplomas": ["MSc Computer Science", "BSc Computer Science"],
        "academic_projects": []
    }


@pytest.fixture
def sample_jd_data():
    """Sample structured JD data (as returned by extraction)."""
    return {
        "job_title": "Senior Full-Stack Developer",
        "company_name": "InnovateTech Solutions",
        "location": "San Francisco, CA",
        "job_type": "Full-time",
        "responsibilities": [
            "Design and implement scalable web applications",
            "Work with React and Node.js",
            "Develop RESTful APIs"
        ],
        "skills": ["JavaScript", "TypeScript", "React", "Node.js", "PostgreSQL", "Git"],
        "experience_level": "4-6 years",
        "education_requirements": ["Bachelor's degree in Computer Science"]
    }


@pytest.fixture
def mock_embedding():
    """Mock embedding vector (384 dimensions)."""
    np.random.seed(42)  # For reproducibility
    return np.random.rand(384).astype(np.float32)


@pytest.fixture
def sample_cv_entity(sample_cv_data, sample_cv_text, mock_embedding):
    """Sample CV entity for testing."""
    from src.utils.integration import dict_to_cv
    cv = dict_to_cv(sample_cv_data, sample_cv_text)
    cv.embedding = mock_embedding
    return cv


@pytest.fixture
def sample_jd_entity(sample_jd_data, sample_jd_text, mock_embedding):
    """Sample JD entity for testing."""
    from src.utils.integration import dict_to_jd
    jd = dict_to_jd(sample_jd_data, sample_jd_text)
    jd.embedding = mock_embedding * 0.9  # Slightly different embedding
    return jd


@pytest.fixture
def mock_gemini_cv_response():
    """Mock Gemini API response for CV extraction."""
    return """{
        "name": "John Doe",
        "contact": {
            "email": "john.doe@example.com",
            "phone": "+1-555-0123"
        },
        "skills": ["Python", "JavaScript", "React", "Node.js"],
        "experience": ["Senior Software Engineer at Tech Corp (2020-2023)"],
        "education": ["Master of Science in Computer Science, Stanford University"],
        "diplomas": ["MSc Computer Science"],
        "academic_projects": []
    }"""


@pytest.fixture
def mock_gemini_jd_response():
    """Mock Gemini API response for JD extraction."""
    return """{
        "job_title": "Senior Full-Stack Developer",
        "company_name": "InnovateTech Solutions",
        "location": "San Francisco, CA",
        "job_type": "Full-time",
        "responsibilities": ["Design and implement scalable web applications"],
        "skills": ["JavaScript", "TypeScript", "React", "Node.js"],
        "experience_level": "4-6 years",
        "education_requirements": ["Bachelor's degree in Computer Science"]
    }"""
