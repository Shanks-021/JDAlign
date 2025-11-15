"""
Simple JD and Resume Gap Analyzer
Just compares JD text with resume text using Gemini
"""

import os
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import certifi  # Add this import

load_dotenv()

import os
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import certifi  # Add this import

load_dotenv()

def extract_jd_from_url(url):
    """
    Extract job description from a URL
    
    Args:
        url: URL of the job posting (LinkedIn, Indeed, company website, etc.)
        
    Returns:
        Job description text
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Add verify parameter with certifi's certificate bundle
        response = requests.get(url, headers=headers, timeout=10, verify=certifi.where())
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception as e:
        raise ValueError(f"Failed to extract JD from URL: {str(e)}")

# ...existing code...

def extract_resume_text(pdf_path):
    """Extract text from PDF resume"""
    with open(pdf_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text


def analyze_jd_resume(jd_text, resume_text):
    """
    Simple LLM call to compare JD and resume and find gaps
    
    Args:
        jd_text: Job description text
        resume_text: Resume text
        
    Returns:
        Analysis from Gemini
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")
    
    genai.configure(api_key=api_key)
    
    prompt = f"""
    You are a technical recruiter analyzing a candidate's resume against a job description.
    
    JOB DESCRIPTION:
    {jd_text}
    
    CANDIDATE'S RESUME:
    {resume_text}
    
    TASK: Compare TECHNICAL SKILLS ONLY between the JD and Resume.
    
    Focus exclusively on:
    - Programming languages
    - Frameworks and libraries
    - Tools and technologies
    - Databases
    - Cloud platforms
    - APIs and integrations
    - Version control systems
    - CI/CD tools
    - Testing frameworks
    
    Provide your analysis in this format:
    
    ## MISSING TECHNICAL SKILLS
    List each technical skill, technology, or tool mentioned in the JD but NOT found in the resume.
    For each missing skill, suggest a specific project the candidate can build to demonstrate that skill.
    
    Format:
    - **[Missing Skill/Technology]**: Brief project idea (1-2 sentences) that would demonstrate this skill effectively.
    
    Example:
    - **Go Programming**: Build a REST API service in Go with CRUD operations, Docker containerization, and unit tests.
    - **Redis**: Create a caching layer for a web application using Redis to improve response times.
    
    ## TECHNICAL FIT SCORE: X/100
    Score based purely on technical skill alignment (consider both presence and depth of skills).
    
    ## PROJECT RECOMMENDATIONS SUMMARY
    Provide 3-5 priority projects the candidate should build to maximize their fit for this role.
    List them in order of importance based on the JD requirements.
    
    Format each as:
    1. **[Project Name]**: [Brief description] - Covers: [Skills this project would demonstrate]
    
    Keep your analysis objective and focused on technical competencies only. Ignore soft skills, cultural fit, or non-technical requirements.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    return response.text


def main():
    # Your JD text
    jd_text = """
    About the job

About Maxim
At Maxim, we are building the evaluation infrastructure to help modern AI teams bring their products to market faster, with the quality and reliability needed for real-world use.

Backed by an amazing set of investors and are building our core team to empower development teams to ship high-quality AI agents, faster. 

About the role 
At the heart of this role is Bifrost. Bifrost is the fastest, fully open-source LLM gateway. Written in Go, it is a product of deep engineering focus with performance optimized at every level of the architecture. It supports 1000+ models across providers via a single API.
In just a few months since launch, Bifrost has quickly gained traction with leading enterprises and now we're looking to bring on someone who can scale it even faster and help turn complex AI infrastructure into a simple, invisible superpower for AI teams globally.

Responsibilities
You'll be working across two tracks:

Open-source Development: 
* Maintain, improve and expand the Bifrost OSS codebase. 
* Engage with the OSS community by reviewing contributions, triaging issues, and incorporating feedback.
* Ensure high code quality, clear documentation and smooth developer onboarding for Bifrost contributors.
* Ensure Bifrost offers an intuitive, efficient and enjoyable user experience - balancing high performance with ease of use.

Enterprise Features: 
* Build new features on top of our open-source platform that help it grow smoothly, connect easily with other tools and give users clear insights into how everything is running.
* Work closely with our enterprise users to understand their needs and turn them into practical, reliable features.
* Collaborate with product/design to make sure these features are not only effective but also easy and pleasant to use, blending naturally into the overall experience.

Tech Stack
* Primary: Go
* Secondary: Typescript + NextJS

About You
* You have 2-4 years of experience in software development, with a strong foundation in Go programming patterns.
* You are a generalist comfortable with working across different databases.
* You bring solid software engineering principles and know how to ship clean, maintainable code.
* You enjoy working in early-stage environments where ownership and autonomy are key.
* You've built and shipped an AI-related project. 
* (Share it in your application - please include a link to the most impactful project you have built.)
* Above all, you take pride in thoughtful engineering that balances quality, performance, and user experience.

Nice to Haves
* You've worked with Typescript and have used NextJS.
* You've built SDKs or tools designed for external developers.
* You've previously worked at or founded a startup.
* You've worked closely with design, product or customer-facing teams to ship features.

Compensation & Benefits
At Maxim, we provide competitive compensation – great salary, robust equity grants, and other perks including health benefits and AI stipend. Beyond compensation, we constantly strive to build an empowering workplace with high-degree of autonomy, take-charge ownership and dynamic opportunities for growth, all as Maxim continues to soar!

Location: Bengaluru, on-site
    """
    
    # Extract resume from PDF
    pdf_path = "Ojas_resume.pdf"
    resume_text = extract_resume_text(pdf_path)
    
    print("Analyzing JD vs Resume...\n")
    
    # Get analysis
    jd_textq = extract_jd_from_url("https://www.linkedin.com/jobs/view/4309753456/?alternateChannel=search&eBP=BUDGET_EXHAUSTED_JOB&refId=lMlD66LtBLlV4rqwvLP8Ug%3D%3D&trackingId=PBpn%2Bc9aE%2BljT%2BU5k7gVoA%3D%3D")
    print(jd_textq)
    analysis = analyze_jd_resume(jd_textq, resume_text)
    
    print(analysis)
    
    # Save to file
    with open("analysis_report.txt", "w") as f:
        f.write(analysis)
    print("\n✅ Analysis saved to analysis_report.txt")

if __name__ == "__main__":
    main()

