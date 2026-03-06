import streamlit as st
import subprocess
import os
from docx import Document
import re
import tempfile
import shutil

# Template path
TEMPLATE = "templates/scholarly.typ"


# -----------------------------
# Check Typst installation
# -----------------------------
def check_typst():

    if shutil.which("typst") is None:
        st.error("❌ Typst is not installed on this server.")
        st.stop()

    result = subprocess.run(
        ["typst", "--version"],
        capture_output=True,
        text=True
    )

    st.success(f"Typst detected: {result.stdout.strip()}")


# -----------------------------
# Parse DOCX
# -----------------------------
def parse_docx(file):

    doc = Document(file)
    paragraphs = []

    for para in doc.paragraphs:

        text = para.text.strip()

        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


# -----------------------------
# Sanitize text for Typst
# -----------------------------
def sanitize_text(text):

    text = re.sub(r'#', r'\\#', text)
    text = re.sub(r'\{', r'\\{', text)
    text = re.sub(r'\}', r'\\}', text)

    return text


# -----------------------------
# Create Typst file
# -----------------------------
def create_typst_file(content, typ_path):

    with open(TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()

    final = template.replace("{{MANUSCRIPT_CONTENT}}", content)

    with open(typ_path, "w", encoding="utf-8") as f:
        f.write(final)


# -----------------------------
# Compile PDF
# -----------------------------
def compile_pdf(typ_path, pdf_path):

    result = subprocess.run(
        ["typst", "compile", typ_path, pdf_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        st.error(result.stderr)
        return False

    return True


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Automated Typesetter")

st.write(
    "Upload a DOCX manuscript and generate a print-ready PDF using Typst."
)

# Verify Typst
check_typst()

uploaded_file = st.file_uploader("Upload DOCX file", type=["docx"])


if uploaded_file:

    if st.button("Generate PDF"):

        st.info("Processing manuscript...")

        # Step 1: Parse DOCX
        manuscript = parse_docx(uploaded_file)

        # Step 2: Clean characters
        manuscript = sanitize_text(manuscript)

        # Step 3: Temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:

            typ_file = os.path.join(temp_dir, "book.typ")
            pdf_file = os.path.join(temp_dir, "book.pdf")

            # Step 4: Create Typst file
            create_typst_file(manuscript, typ_file)

            # Step 5: Compile PDF
            success = compile_pdf(typ_file, pdf_file)

            if success and os.path.exists(pdf_file):

                st.success("PDF generated successfully!")

                with open(pdf_file, "rb") as f:

                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name="typeset_book.pdf",
                        mime="application/pdf"
                    )

            else:
                st.error("PDF generation failed.")
