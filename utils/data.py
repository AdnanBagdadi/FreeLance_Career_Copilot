import streamlit as st

DEFAULT_PROFILE = {
    "name": "Muaaz Shaikh",
    "title": "MSc Data Science | Python & Machine Learning",
    "bio": "Data Science postgraduate focused on machine learning, analytics, Python and AI-powered applications.",
    "skills": ["Python", "Machine Learning", "Pandas", "Scikit-learn", "SQL",
               "Power BI", "Streamlit", "NLP", "Data Visualization"],
    "experience": "Intermediate",
    "rate": 30,
}

DEFAULT_PORTFOLIO = [
    {"id": 1, "title": "Customer Churn Prediction Pipeline",
     "description": "End-to-end churn model with EDA, feature engineering and a Streamlit results dashboard.",
     "skills": ["Python", "Machine Learning", "Pandas", "Scikit-learn", "Streamlit"]},
    {"id": 2, "title": "Retail Sales Power BI Dashboard",
     "description": "Interactive KPI dashboard with DAX measures for a multi-store retail dataset.",
     "skills": ["Power BI", "SQL", "Data Visualization", "Excel"]},
    {"id": 3, "title": "Support Ticket Text Classifier",
     "description": "NLP pipeline (TF-IDF + classical ML) to auto-tag incoming support tickets.",
     "skills": ["Python", "NLP", "Scikit-learn", "Data Analysis"]},
]


def init_state():
    if "profile" not in st.session_state:
        st.session_state.profile = DEFAULT_PROFILE.copy()
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = [p.copy() for p in DEFAULT_PORTFOLIO]
    if "job_history" not in st.session_state:
        st.session_state.job_history = []
    if "current_analysis" not in st.session_state:
        st.session_state.current_analysis = None
    if "applications" not in st.session_state:
        st.session_state.applications = []
    if "generated_proposal" not in st.session_state:
        st.session_state.generated_proposal = ""
