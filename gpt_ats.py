import streamlit as st
import json
import os
import time
from openai import OpenAI
import html

# Page configuration
st.set_page_config(
    page_title="ATS Score Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Overall theme improvements */
    .main {
        background-color: #121212;
        color: #f0f0f0;
    }
    
    /* Make input boxes more compact and styled */
    .stTextArea textarea {
        height: 220px !important;
        font-size: 0.9rem !important;
        background-color: #1e1e1e;
        border: 1px solid #333;
        border-radius: 8px;
    }
    
    /* Card styling */
    .card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    
    .card-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #444;
        color: #fff;
    }
    
    /* Score circle styling */
    .score-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .score-circle {
        position: relative;
        width: 180px;
        height: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
    }
    
    .score-background {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: #1e1e1e;
        box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5);
        border: 1px solid #333;
    }
    
    .score-value {
        position: relative;
        z-index: 2;
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        line-height: 1.2;
    }
    
    .score-message {
        position: relative;
        z-index: 2;
        font-size: 14px;
        text-align: center;
        margin-top: 5px;
        max-width: 140px;
    }
    
    /* Custom button styling */
    .download-btn {
        background-color: #2d3035;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
        text-align: center;
        display: inline-block;
        margin-top: 15px;
    }
    
    .download-btn:hover {
        background-color: #3d4045;
    }
    
    /* Skills list styling */
    .skills-container {
        margin-top: 20px;
    }
    
    .skills-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        font-size: 18px;
        font-weight: bold;
    }
    
    .skills-header .icon {
        margin-right: 10px;
        font-size: 20px;
    }
    
    .skills-list {
        list-style-type: none;
        padding-left: 15px;
    }
    
    .skills-list li {
        margin-bottom: 10px;
        padding: 8px 12px;
        background-color: #2d3035;
        border-radius: 5px;
        display: flex;
        align-items: center;
    }
    
    .skills-list li::before {
        content: "•";
        margin-right: 10px;
        color: #888;
    }
    
    .matching-skill li {
        border-left: 3px solid #4CAF50;
    }
    
    .missing-skill li {
        border-left: 3px solid #F44336;
    }
    
    /* Analysis section styling */
    .analysis-text {
        line-height: 1.6;
        margin-top: 10px;
    }
    
    /* Horizontal divider */
    .divider {
        height: 1px;
        background-color: #444;
        margin: 30px 0;
    }
    
    /* Title styling */
    .title-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .title-icon {
        font-size: 32px;
        margin-right: 15px;
        color: #4CAF50;
    }
    
    .title-text {
        font-size: 24px;
        font-weight: bold;
    }
    
    /* Skill icon colors */
    .green-icon {
        color: #4CAF50;
    }
    
    .red-icon {
        color: #F44336;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown("""
<div class="title-container">
    <div class="title-icon">📊</div>
    <div class="title-text">ATS Score Calculator</div>
</div>
<p>This application analyzes resumes against job descriptions to generate an ATS compatibility score.
Enter your resume and a job description to see how well they match.</p>
""", unsafe_allow_html=True)

# Initialize Together client with API key
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

client = OpenAI()

# Function to calculate ATS score with better error handling
def calculate_ats_score(resume_data, job_description):
    system_prompt = f"""
    You are an expert ATS (Applicant Tracking System) analyst with years of experience in HR and recruitment.
    
    Analyze the following resume against the job description, giving a score between 0-100 by focusing specifically on these key components:
    1. Skills - Technical and soft skills that match the job description
    2. Education - Relevance of degrees, certifications, and educational background 
    3. Work Experience - Relevant work history, roles, responsibilities, and achievements alligned with job description
    4. Projects (if present) - Personal or professional projects that demonstrate relevant abilities alligned with job description
    
    Resume details:
    {resume_data}
    
    Job Description:
    {job_description}
    
    Follow this detailed analysis process:
    
    1. First, extract all explicit requirements and preferences from the job description
    2. For each key component, perform a systematic comparison:
    
       SKILLS ANALYSIS:
       - List all technical and soft skills mentioned in the job description
       - Compare against skills listed in the resume
    
       EDUCATION ANALYSIS:
       - Identify education requirements in the job description
       - Check if the candidate's degrees and certifications meet the requirements 
       - Check certifications (if any) are aligned with job requirements
       
       EXPERIENCE ANALYSIS:
       - Assess relevance of previous roles to the job description
       - Check if the roles and responsibilities are clearly aligned with the job description
    
       PROJECTS ANALYSIS (if projects are present in the resume):
       - Assess technical alignment of projects with job description
       - Assess if project skills align with job description requirements
    
    ***IMPORTANT: This task requires MAXIMUM ACCURACY. You must carefully and thoroughly analyze the resume and job description before providing any scores. Take a methodical approach, comparing each element of the resume against the job requirements in detail.
    Your final score should be only on the basis of how much candidate resume is alligned with the job description.***
    
    Provide the output in EXACTLY the following JSON format:
    
    ```json
    {{
        "overall_score": "a number between 0-100 representing overall match of resume with job description",
        "analysis": "Brief analysis text here...",
        "matching_skills": ["Skill 1", "Skill 2"],
        "missing_skills": ["Skill 3", "Skill 4" ]
        "Things need to be added on the basis of analysis": "give a summary with all the things that are required to make the resume more alligned with the job description"    }}
    ```
    
    Important: You MUST use EXACTLY these keys in your response. Do not add additional keys or change the key names. 
    """
    
    # Create a status placeholder for more detailed progress information
    status_placeholder = st.empty()
    
    try:
        # status_placeholder.info("Initializing API request to Together AI...")
        
        # Set timeout for API call
        start_time = time.time()
        timeout = 120  # 2 minutes timeout
        
        # Make the API call
        status_placeholder.info("Calculating Score, Pleae wait...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert ATS analyzer with a strong commitment to accuracy and detail. Your analysis must be methodical and precise, focusing on skills, education, experience, and projects(if present), your FINAL SCORE should be only on the basis of how well the candidate resume is alligned with the job description"},
                {"role": "user", "content": system_prompt}
            ],
            response_format={"type": "json_object"},
            timeout=timeout
        )
        
        status_placeholder.success("Analysis completed successfully!")
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = str(e)
        status_placeholder.error(f"Error: {error_msg}")
        
        # Provide more helpful error messages based on common issues
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
            st.error("API Key Error: Please check your Together AI API key. The key might be invalid or missing.")
        elif "timeout" in error_msg.lower() or "deadline" in error_msg.lower():
            st.error("Timeout Error: The request took too long to complete. The AI model might be busy. Please try again in a few minutes.")
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            st.error("Connection Error: There was a problem connecting to the Together AI servers. Please check your internet connection.")
        else:
            st.error(f"An unexpected error occurred: {error_msg}\n\nPlease try again or contact support if the issue persists.")
        
        return None

# Function to render the score circle
def render_score_circle(score):
    # Determine color based on score
    if score >= 75:
        color = "#4CAF50"  # Green
        message = "Excellent match!"
    elif score >= 60:
        color = "#FF9800"  # Orange
        message = "Good match with room for improvement"
    else:
        color = "#F44336"  # Red
        message = "Needs significant improvement"
    
    # SVG for circular progress
    circle_radius = 80
    circle_circumference = 2 * 3.14159 * circle_radius
    stroke_dashoffset = circle_circumference - (circle_circumference * score / 100)
    
    html_code = f"""
    <div class="score-container">
        <div class="score-circle">
            <div class="score-background"></div>
            <svg width="180" height="180" viewBox="0 0 180 180" style="position: absolute; transform: rotate(-90deg);">
                <circle r="{circle_radius}" cx="90" cy="90" fill="transparent" stroke="#333" stroke-width="8"></circle>
                <circle r="{circle_radius}" cx="90" cy="90" fill="transparent" 
                    stroke="{color}" stroke-width="8" 
                    stroke-dasharray="{circle_circumference}" 
                    stroke-dashoffset="{stroke_dashoffset}"
                    stroke-linecap="round"></circle>
            </svg>
            <div style="position: relative; z-index: 2; text-align: center;">
                <div class="score-value" style="color: {color};">{score}/100</div>
                <div class="score-message" style="color: {color};">{message}</div>
            </div>
        </div>
    </div>
    """
    return html_code

# Sidebar for file upload and additional options
with st.sidebar:
    st.header("📄 Upload Files")
    resume_file = st.file_uploader("Upload Resume (Optional)", type=["pdf", "docx", "txt"])
    job_file = st.file_uploader("Upload Job Description (Optional)", type=["pdf", "docx", "txt"])
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool helps you optimize your resume for Applicant Tracking Systems.
    It analyzes how well your resume matches a specific job description.
    """)

# Create a container for inputs
input_container = st.container()

# Create a container for results that will be shown/hidden
results_container = st.container()

# Input section with improved styling
with input_container:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Enter Your Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resume")
        if resume_file is not None:
            # Here you would add code to extract text from uploaded file
            st.info("File uploaded! In a complete application, text would be extracted automatically.")
            resume_text = "Sample resume text from uploaded file"
        else:
            resume_text = ""
        
        resume_text = st.text_area(
            "Paste your resume here:",
            height=220,
            placeholder="Paste your complete resume text here...",
            value=resume_text
        )
    
    with col2:
        st.subheader("Job Description")
        if job_file is not None:
            # Here you would add code to extract text from uploaded file
            st.info("File uploaded! In a complete application, text would be extracted automatically.")
            job_description_text = "Sample job description from uploaded file"
        else:
            job_description_text = ""
        
        job_description_text = st.text_area(
            "Paste the job description here:",
            height=220,
            placeholder="Paste the complete job description here...",
            value=job_description_text
        )
    
    # Analyze button
    if st.button("Calculate ATS Score", type="primary", use_container_width=True):
        if not resume_text or not job_description_text:
            st.error("Please provide both a resume and job description.")
        else:
            st.info("Analyzing Resume and Job Description...")
            try:
                # Store the result in session state
                result = calculate_ats_score(resume_text, job_description_text)
                if result:
                    st.session_state.ats_result = result
                    # st.success("Analysis complete!")
            except Exception as e:
                st.error(f"Failed to connect to API: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Horizontal separator
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Results section with improved layout and styling
with results_container:
    if 'ats_result' in st.session_state:
        try:
            # Parse the JSON result
            result_data = json.loads(st.session_state.ats_result)
            
            # Header for results section
            st.markdown("""
            <h2 style="text-align: center; margin-bottom: 30px;">
                <span style="color: #4CAF50;">📊</span> ATS Analysis Results
            </h2>
            """, unsafe_allow_html=True)
            
            # New improved layout - Score and Analysis on left, Skills on right
            left_col, right_col = st.columns([1, 1], gap="large")
            
            # LEFT COLUMN - Score and Analysis
            with left_col:
                # Score card with circular visualization
                st.markdown('<div class="card">', unsafe_allow_html=True)
                score = int(result_data["overall_score"])
                st.markdown(render_score_circle(score), unsafe_allow_html=True)
                
                # Download button with custom styling
                centered_col = st.columns([1, 2, 1])[1]
                with centered_col:
                    st.download_button(
                        label="Download Analysis",
                        data=st.session_state.ats_result,
                        file_name="ats_analysis.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Analysis card
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">Analysis</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="analysis-text">{result_data["analysis"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # RIGHT COLUMN - Skills Analysis
            with right_col:
                # Skills card
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-header">Skills Analysis</div>', unsafe_allow_html=True)
                
                # Matching Skills with custom styling
                st.markdown("""
                <div class="skills-container">
                    <div class="skills-header">
                        <span class="icon green-icon">✓</span> Matching Skills
                    </div>
                    <ul class="skills-list matching-skill">
                """, unsafe_allow_html=True)
                
                if result_data["matching_skills"]:
                    for skill in result_data["matching_skills"]:
                        st.markdown(f"<li>{html.escape(skill)}</li>", unsafe_allow_html=True)
                else:
                    st.write("No matching skills found.")
                
                st.markdown('</ul></div>', unsafe_allow_html=True)
                
                # Missing Skills with custom styling
                st.markdown("""
                <div class="skills-container">
                    <div class="skills-header">
                        <span class="icon red-icon">✗</span> Missing Skills
                    </div>
                    <ul class="skills-list missing-skill">
                """, unsafe_allow_html=True)
                
                if result_data["missing_skills"]:
                    for skill in result_data["missing_skills"]:
                        st.markdown(f"<li>{html.escape(skill)}</li>", unsafe_allow_html=True)
                else:
                    st.write("No missing skills identified.")
                
                st.markdown('</ul></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
        except json.JSONDecodeError:
            st.error("Error parsing the analysis result. Please try again.")
        except KeyError as e:
            st.error(f"Missing expected data in the result: {e}")
    else:
        # Show empty state
        st.markdown("""
        <div style="text-align: center; padding: 50px 20px; color: #888;">
            <i style="font-size: 48px;">📝</i>
            <p style="margin-top: 15px; font-size: 18px;">
                Enter your resume and job description above and click 'Analyze Resume' to see results here.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Run the main application
if __name__ == "__main__":
    pass  # Streamlit already executes the script from top to bottom

