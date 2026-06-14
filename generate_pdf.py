import os
import glob
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, KeepTogether, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Draw header (except first page)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Oblique", 8)
            self.setFillColor(colors.HexColor("#4b5563"))
            self.drawString(54, 750, "SutraLang: Paninian Computational Linguistics for AI Agents")
            self.setStrokeColor(colors.HexColor("#e5e7eb"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Draw footer
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4b5563"))
        self.drawRightString(558, 40, f"Page {self._pageNumber} of {page_count}")
        self.drawString(54, 40, "Anant Anaadi Sovereign Technology Wing")
        self.setStrokeColor(colors.HexColor("#e5e7eb"))
        self.setLineWidth(0.5)
        self.line(54, 52, 558, 52)

def build_pdf():
    # Setup document
    pdf_path = "/sdcard/Download/SutraLang/sutralang_research_paper.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles matching our academic aesthetic
    styles.add(ParagraphStyle(
        name='DocTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        alignment=1, # Center
        spaceAfter=15
    ))

    styles.add(ParagraphStyle(
        name='AuthorStyle',
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        alignment=1, # Center
        spaceAfter=20
    ))

    styles.add(ParagraphStyle(
        name='AbstractText',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        alignment=4, # Justified
        leftIndent=20,
        rightIndent=20
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=18,
        spaceAfter=8,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='SubSectionHeader',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name='BodyTextCustom',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8,
        alignment=4 # Justified
    ))

    styles.add(ParagraphStyle(
        name='CaptionStyle',
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#4b5563"),
        alignment=1, # Center
        spaceBefore=6,
        spaceAfter=15
    ))

    styles.add(ParagraphStyle(
        name='RefStyle',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#4b5563"),
        leftIndent=15,
        firstLineIndent=-15,
        spaceAfter=6
    ))

    story = []

    # Read research paper markdown
    md_path = "/sdcard/Download/SutraLang/sutralang_research_paper.md"
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into sections/paragraphs
    lines = content.split('\n')
    in_abstract = False
    
    # Track which image file maps to which figure index
    # We will look up PNG files in the Download/SutraLang directory
    img_files = glob.glob("/sdcard/Download/SutraLang/*.png")
    
    # Map keywords in captions to file paths
    # Figure 1: Architecture
    # Figure 2: Paninian principles
    # Figure 3: REPL screen / prototype
    # Figure 4: Graph/Complexity
    # Figure 5: Comparison / Before-After
    def find_image_by_keyword(keyword):
        for img in img_files:
            if keyword in img.lower():
                return img
        return None

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Header Title
        if line.startswith("# ") and not line.startswith("##"):
            title_text = line.replace("# ", "")
            story.append(Paragraph(title_text, styles['DocTitle']))
            # Next line contains authors
            i += 1
            author_line = lines[i].strip()
            # Clean md bold/italics
            author_line = author_line.replace("**", "").replace("*", "")
            # Next line contains email
            i += 1
            email_line = lines[i].strip().replace("`", "")
            story.append(Paragraph(f"{author_line}<br/>{email_line}", styles['AuthorStyle']))
            story.append(Spacer(1, 15))
            i += 1
            continue

        # Abstract block
        if line.startswith("## Abstract"):
            in_abstract = True
            story.append(Paragraph("<b>Abstract</b>", styles['SectionHeader']))
            i += 1
            abstract_text = ""
            while i < len(lines) and not lines[i].startswith("---"):
                abstract_text += lines[i].strip() + " "
                i += 1
            story.append(Paragraph(abstract_text, styles['AbstractText']))
            story.append(Spacer(1, 20))
            in_abstract = False
            i += 1
            continue

        # Section separation line
        if line.startswith("---"):
            i += 1
            continue

        # Section Headers
        if line.startswith("## ") and not line.startswith("###"):
            sec_title = line.replace("## ", "")
            story.append(Paragraph(sec_title, styles['SectionHeader']))
            i += 1
            continue

        # Subsection Headers
        if line.startswith("### "):
            subsec_title = line.replace("### ", "")
            story.append(Paragraph(subsec_title, styles['SubSectionHeader']))
            i += 1
            continue

        # Image/Figure parsing
        # Matches: ![Caption text](image_path)
        img_match = re.match(R"^\!\[(.*?)\]\((.*?)\)$", line)
        if img_match:
            caption = img_match.group(1)
            # Find the actual local png file in the download directory
            actual_img_path = None
            if "architecture" in caption.lower():
                actual_img_path = find_image_by_keyword("architecture")
            elif "principles" in caption.lower():
                actual_img_path = find_image_by_keyword("principles")
            elif "repl" in caption.lower() or "prototype" in caption.lower():
                actual_img_path = find_image_by_keyword("repl")
            elif "graph" in caption.lower() or "complexity" in caption.lower():
                actual_img_path = find_image_by_keyword("graph")
            elif "comparison" in caption.lower() or "before" in caption.lower():
                actual_img_path = find_image_by_keyword("comparison")

            if actual_img_path and os.path.exists(actual_img_path):
                # Add scaled image to fit width (480 points)
                # Keep original aspect ratio
                img_flow = Image(actual_img_path, width=4.5*inch, height=4.5*inch)
                story.append(KeepTogether([
                    Spacer(1, 10),
                    img_flow,
                    Paragraph(caption, styles['CaptionStyle']),
                    Spacer(1, 10)
                ]))
            i += 1
            continue

        # Bullet lists
        if line.startswith("* "):
            bullet_text = line.replace("* ", "• ")
            # Check if bold starts
            bullet_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", bullet_text)
            story.append(Paragraph(bullet_text, styles['BodyTextCustom']))
            i += 1
            continue

        # References list
        if len(story) > 0 and isinstance(story[-1], Paragraph) and "References" in lines[i-1]:
            # Treat subsequent items as references
            while i < len(lines):
                ref_line = lines[i].strip()
                if ref_line:
                    # Clean number formatting e.g., 1. Name -> 1. Name
                    ref_clean = re.sub(r"^\d+\.\s+", "", ref_line)
                    ref_num = re.search(r"^(\d+)\.\s+", ref_line)
                    prefix = f"[{ref_num.group(1)}] " if ref_num else "• "
                    story.append(Paragraph(prefix + ref_clean, styles['RefStyle']))
                i += 1
            break

        # Standard Body Text / Equations
        body_text = line
        body_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", body_text)
        # Parse inline latex equation mappings
        body_text = re.sub(r"\$\$(.*?)\$\$", r"<font face='Courier'>\1</font>", body_text)
        body_text = re.sub(r"\$(.*?)\$", r"<font face='Courier'>\1</font>", body_text)
        
        story.append(Paragraph(body_text, styles['BodyTextCustom']))
        i += 1

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF successfully compiled and saved to /sdcard/Download/SutraLang/sutralang_research_paper.pdf")

if __name__ == "__main__":
    build_pdf()
