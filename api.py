from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import uvicorn
from jd_resume_analyzer import analyze_jd_resume, extract_jd_from_url, extract_resume_text

app = FastAPI(title="JD Resume Analyzer API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "JD Resume Analyzer API", "status": "running"}

@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(..., description="Resume PDF file"),
    jd_text: str = Form(None, description="Job description text"),
    jd_url: str = Form(None, description="Job description URL")
):
    """
    Analyze resume against job description.
    Accepts either jd_text OR jd_url (not both).
    """
    try:
        # Validate inputs
        if not jd_text and not jd_url:
            raise HTTPException(
                status_code=400, 
                detail="Either jd_text or jd_url must be provided"
            )
        
        if jd_text and jd_url:
            raise HTTPException(
                status_code=400,
                detail="Provide either jd_text or jd_url, not both"
            )
        
        # Validate resume file
        if not resume.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Resume must be a PDF file"
            )
        
        # Get JD text
        if jd_url:
            print(f"Extracting JD from URL: {jd_url}")
            jd_content = extract_jd_from_url(jd_url)
        else:
            jd_content = jd_text
        
        # Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await resume.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Extract resume text
            print("Extracting text from resume...")
            resume_text = extract_resume_text(tmp_path)
            
            # Analyze
            print("Analyzing with Gemini AI...")
            analysis = analyze_jd_resume(jd_content, resume_text)
            
            return {
                "success": True,
                "analysis": analysis,
                "resume_filename": resume.filename
            }
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
