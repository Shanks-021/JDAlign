import streamlit as st
import requests
import tempfile
import os
import certifi
# Page configuration
st.set_page_config(
    page_title="JD Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000/analyze"

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🎯 JD Resume Analyzer")
st.markdown("Analyze technical skills gap between Job Descriptions and Resumes using AI")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This tool analyzes your resume against a job description and provides:
    - Missing technical skills
    - Technical fit score
    - Project recommendations
    
    **Powered by Google Gemini AI**
    """)
    
    st.divider()
    
    st.header("🔧 Settings")
    show_debug = st.checkbox("Show debug info", value=False)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📋 Job Description")
    
    # Tab for JD input method
    jd_tab1, jd_tab2 = st.tabs(["📝 Paste Text", "🔗 From URL"])
    
    with jd_tab1:
        jd_text = st.text_area(
            "Paste job description here",
            height=300,
            placeholder="Paste the complete job description including requirements, responsibilities, and tech stack..."
        )
    
    with jd_tab2:
        jd_url = st.text_input(
            "Enter job posting URL",
            placeholder="https://www.linkedin.com/jobs/view/..."
        )

with col2:
    st.header("📄 Resume")
    
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF only)",
        type=['pdf'],
        help="Upload your resume in PDF format"
    )
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        st.info(f"📦 File size: {uploaded_file.size / 1024:.2f} KB")

# Analyze button
st.divider()

analyze_button = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)

if analyze_button:
    # Validation
    errors = []
    
    if not uploaded_file:
        errors.append("❌ Please upload a resume PDF")
    
    if not jd_text and not jd_url:
        errors.append("❌ Please provide either job description text or URL")
    
    if jd_text and jd_url:
        errors.append("❌ Please provide either text OR URL, not both")
    
    if errors:
        for error in errors:
            st.error(error)
    else:
        # Show progress
        with st.spinner("🔍 Analyzing your resume... This may take 10-30 seconds"):
            try:
                # Prepare the request
                files = {
                    'resume': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')
                }
                
                data = {}
                if jd_url:
                    data['jd_url'] = jd_url
                else:
                    data['jd_text'] = jd_text
                
                if show_debug:
                    st.write("**Debug: Request data**")
                    st.json({"jd_url": jd_url if jd_url else None, "jd_text_length": len(jd_text) if jd_text else 0})
                
                # Make API request
                response = requests.post(API_URL, files=files, data=data)
                
                if show_debug:
                    st.write("**Debug: Response status**")
                    st.write(f"Status code: {response.status_code}")
                
                # Handle response
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ Analysis completed successfully!")
                    
                    # Display results
                    st.divider()
                    st.header("📊 Analysis Results")
                    
                    # Show analysis in a nice format
                    st.markdown(result['analysis'])
                    
                    # Download button
                    st.divider()
                    st.download_button(
                        label="📥 Download Analysis Report",
                        data=result['analysis'],
                        file_name="resume_analysis.md",
                        mime="text/markdown"
                    )
                    
                else:
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.error(f"❌ Analysis failed: {error_detail}")
                    
                    if show_debug:
                        st.write("**Debug: Full response**")
                        st.json(response.json())
                        
            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to the backend server. Make sure it's running on http://localhost:8000")
                st.info("💡 Start the backend with: `uvicorn api:app --reload`")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                if show_debug:
                    st.exception(e)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Made with ❤️ using Streamlit & FastAPI</p>
        <p>Powered by Google Gemini AI</p>
    </div>
""", unsafe_allow_html=True)