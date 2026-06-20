"""
infrastructure/scripts/init_resume.py
Writes the base resume JSON. Run once after cloning.
"""
import os, json

RESUME = {
    "name": "Nathan Sam",
    "email": "Yemsam17@yahoo.com",
    "phone": "860-931-3627",
    "location": "New Britain, CT",
    "linkedin": "https://linkedin.com/in/nathan-sam-42510123b",
    "github": "",
    "summary": "Cybersecurity professional with 2 years of health IT experience pursuing an MSc in Artificial Intelligence, with applied experience building intelligent automation systems. Proficient in Python, machine learning, and data-driven model development.",
    "education": [
        {"school": "University of New Haven", "degree": "MSc Artificial Intelligence", "graduation": "Present"},
        {"school": "Central Connecticut State University", "degree": "BS Biology, Cybersecurity Minor", "graduation": "December 2024"}
    ],
    "experience": [
        {"title": "Helpdesk / Tech Support", "company": "AFC Urgent Care", "dates": "October 2023 - Present",
         "bullets": [
             "Delivered Tier 1/2 technical support to 200+ end users across multiple clinics with a 90%+ first-call resolution rate using ServiceNow",
             "Reduced average ticket response time through systematic issue tracking and proactive documentation",
             "Strengthened endpoint security posture by administering patches and supporting VPN, Wi-Fi, and endpoint protection deployment"
         ]}
    ],
    "skills": {
        "languages": ["Python"],
        "tools": ["ServiceNow"],
        "areas": ["Data Analysis", "Machine Learning", "Endpoint Security", "VPN", "Network Infrastructure", "Incident Response"]
    },
    "certifications": ["CompTIA Security+"],
    "screening": {
        "work_authorization": "No, I am an American Citizen or Permanent Resident.",
        "visa_type": "N/A - US Citizen",
        "availability": "September 1, 2026",
        "salary_expectation": "$65,000 - $100,000",
        "preferred_language": "Python",
        "relocate": "Yes",
        "years_experience": "5",
        "how_heard": "Hiring site",
        "dei_gender": "Male",
        "dei_ethnicity": "Black",
        "dei_age": "25-29"
    },
    "projects": [
        {"name": "Resume Auto-Apply System",
         "description": "Service-oriented job automation platform with Flask API, RQ workers, SQLAlchemy, and Playwright adapters that discovers, scores, tailors, and applies to security, AI, and edge roles across three tracks",
         "technologies": ["Python", "Flask", "RQ", "Redis", "SQLAlchemy", "Playwright", "Claude API", "Docker"]}
    ]
}

os.makedirs("data/resume", exist_ok=True)
with open("data/resume/base_resume.json", "w", encoding="utf-8") as f:
    json.dump(RESUME, f, indent=2)
print("Wrote data/resume/base_resume.json")
