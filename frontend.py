import streamlit as st
import tempfile
import os
from jd_resume_analyzer import analyze_jd_resume, extract_jd_from_url, extract_resume_text

# Page configuration
st.set_page_config(
    page_title="JD Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

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
                # Save uploaded PDF temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_path = tmp_file.name
                
                try:
                    if show_debug:
                        st.write("**Debug: Processing**")
                        st.write(f"Resume file: {uploaded_file.name}")
                        st.write(f"JD source: {'URL' if jd_url else 'Text'}")
                    
                    # Get JD content
                    if jd_url:
                        st.info("📥 Fetching job description from URL...")
                        jd_content = extract_jd_from_url(jd_url)
                    else:
                        jd_content = jd_text
                    
                    # Extract resume text
                    st.info("📄 Extracting text from resume...")
                    resume_text = extract_resume_text(tmp_path)
                    
                    if show_debug:
                        st.write(f"**Resume text length:** {len(resume_text)} characters")
                        st.write(f"**JD text length:** {len(jd_content)} characters")
                    
                    # Analyze
                    st.info("🤖 Analyzing with Gemini AI...")
                    analysis = analyze_jd_resume(jd_content, resume_text)
                    
                    # Display success
                    st.success("✅ Analysis completed successfully!")
                    
                    # Display results
                    st.divider()
                    st.header("📊 Analysis Results")
                    
                    # Show analysis in a nice format
                    st.markdown(analysis)
                    
                    # Download button
                    st.divider()
                    st.download_button(
                        label="📥 Download Analysis Report",
                        data=analysis,
                        file_name="resume_analysis.md",
                        mime="text/markdown"
                    )
                    
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                        
            except ValueError as e:
                st.error(f"❌ Error: {str(e)}")
                if show_debug:
                    st.exception(e)
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                if show_debug:
                    st.exception(e)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Made with ❤️ using Streamlit</p>
        <p>Powered by Google Gemini AI</p>
    </div>
""", unsafe_allow_html=True)