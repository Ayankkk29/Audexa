class CareerGuidance:
    def get_career_assessment_questions(self):
        return [
            "What are your main interests and passions?",
            "What skills do you enjoy using the most?",
            "What kind of work environment do you thrive in?",
            "What are your long-term career goals?",
            "What values are most important to you in a job (e.g., impact, salary, work-life balance)?",
            "What industries or fields are you curious about?",
            "What problems do you enjoy solving?",
            "What are your strengths and weaknesses?",
            "How do you handle stress and challenges at work?",
            "What kind of impact do you want to make with your career?"
        ]

    def get_career_resources(self, resource_type):
        resources = {
            "resume_tips": [
                "Use action verbs to describe achievements.",
                "Quantify your accomplishments with numbers.",
                "Tailor your resume to each job description.",
                "Keep it concise, ideally 1-2 pages.",
                "Proofread carefully for any errors.",
                "Use a clean, professional format.",
                "Include relevant keywords from the job posting."
            ],
            "interview_preparation": [
                "Research the company and the role thoroughly.",
                "Practice common interview questions (STAR method).",
                "Prepare thoughtful questions to ask the interviewer.",
                "Dress professionally and arrive on time.",
                "Send a thank-you note after the interview.",
                "Be confident and enthusiastic.",
                "Listen actively and answer clearly."
            ],
            "job_search_platforms": [
                "LinkedIn",
                "Indeed",
                "Glassdoor",
                "Naukri.com (for India)",
                "Monster.com",
                "AngelList (for startups)",
                "Remote.co (for remote jobs)"
            ],
            "skill_development": [
                "Coursera",
                "Udemy",
                "LinkedIn Learning",
                "edX",
                "Khan Academy",
                "Codecademy",
                "Google Digital Garage"
            ]
        }
        return resources.get(resource_type, [])

    def get_salary_negotiation_tips(self):
        return [
            "Research average salaries for your role and location.",
            "Know your worth and be confident in your ask.",
            "Practice your negotiation script.",
            "Focus on your value and contributions.",
            "Consider the entire compensation package (benefits, bonuses).",
            "Be prepared to walk away if the offer doesn't meet your needs.",
            "Get the offer in writing before accepting."
        ]

    def get_work_life_balance_tips(self):
        return [
            "Set clear boundaries between work and personal life.",
            "Prioritize tasks and learn to say no.",
            "Take regular breaks throughout the day.",
            "Delegate tasks when possible.",
            "Engage in hobbies and activities outside of work.",
            "Ensure you get enough sleep.",
            "Communicate your needs to your employer."
        ]

    def get_industry_insights(self, industry):
        insights = {
            "technology": {
                "trending_roles": ["AI Engineer", "Data Scientist", "Cloud Architect", "Cybersecurity Analyst"],
                "in_demand_skills": ["Python", "Machine Learning", "Cloud Computing", "DevOps", "Data Analytics"],
                "salary_range": "₹6 LPA - ₹30 LPA+",
                "growth_prospects": "High growth, constant innovation"
            },
            "healthcare": {
                "trending_roles": ["Telemedicine Specialist", "Health Informatics Analyst", "Medical Researcher", "Nurse Practitioner"],
                "in_demand_skills": ["Clinical Skills", "Data Analysis", "Patient Care", "Regulatory Knowledge", "Communication"],
                "salary_range": "₹4 LPA - ₹25 LPA+",
                "growth_prospects": "Steady growth, increasing demand"
            },
            "finance": {
                "trending_roles": ["Financial Analyst", "Investment Banker", "FinTech Specialist", "Risk Manager"],
                "in_demand_skills": ["Financial Modeling", "Data Analysis", "Blockchain", "Regulatory Compliance", "Market Research"],
                "salary_range": "₹5 LPA - ₹35 LPA+",
                "growth_prospects": "Moderate to high growth, evolving with technology"
            },
            "marketing": {
                "trending_roles": ["Digital Marketing Manager", "Content Strategist", "SEO Specialist", "Social Media Manager"],
                "in_demand_skills": ["SEO/SEM", "Content Creation", "Social Media Marketing", "Data Analytics", "CRM"],
                "salary_range": "₹3 LPA - ₹15 LPA+",
                "growth_prospects": "High growth, especially in digital domains"
            }
        }
        return insights.get(industry.lower(), {"message": "No specific insights available for this industry yet."})

career_guidance = CareerGuidance()
