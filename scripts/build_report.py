"""Gera o PDF do relatório editável em Markdown e das capturas reais."""
import re
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Preformatted

ROOT = Path(__file__).resolve().parents[1]


def build():
    output = ROOT / "output/pdf/relatorio-academico.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BodyPT", fontName="Helvetica", fontSize=10.5, leading=15, spaceAfter=9))
    styles.add(ParagraphStyle(name="TitlePT", fontName="Helvetica-Bold", fontSize=22, leading=28, alignment=TA_CENTER, spaceAfter=24))
    styles.add(ParagraphStyle(name="SectionPT", fontName="Helvetica-Bold", fontSize=15, leading=20, spaceAfter=14))
    styles.add(ParagraphStyle(name="SubPT", fontName="Helvetica-Bold", fontSize=11, leading=16, spaceAfter=8))
    styles.add(ParagraphStyle(name="CaptionPT", fontSize=9, leading=12, spaceAfter=12, textColor=colors.HexColor("#334155")))
    styles.add(ParagraphStyle(name="CodePT", fontName="Courier", fontSize=7.5, leading=10, spaceAfter=12))
    story = []
    source = (ROOT / "docs/relatorio.md").read_text(encoding="utf-8-sig")
    for page_number, page in enumerate(source.split("\n---\n")):
        story.append(PageBreak() if page_number else Spacer(1, 2*cm))
        for block in re.split(r"\n\s*\n", page.strip()):
            if block.startswith("```"):
                story.append(Preformatted("\n".join(block.splitlines()[1:-1]), styles["CodePT"]))
                continue
            if block.startswith("!["):
                match = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", block)
                if not match:
                    raise ValueError("Imagem Markdown inválida")
                image = Image(str(ROOT / "docs" / match.group(2)))
                scale = min(15*cm/image.imageWidth, 13.4*cm/image.imageHeight)
                image.drawWidth = image.imageWidth * scale
                image.drawHeight = image.imageHeight * scale
                story.extend([image, Spacer(1, 8), Paragraph(escape(match.group(1)), styles["CaptionPT"])])
                continue
            style = "BodyPT"
            for prefix, name in [("# ","TitlePT"),("## ","SectionPT"),("### ","SubPT")]:
                if block.startswith(prefix):
                    block, style = block[len(prefix):], name
                    break
            safe = escape(block.replace("→", "->")).replace("\n", "<br/>")
            safe = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", safe)
            safe = re.sub(r"`(.*?)`", r"<font name='Courier'>\1</font>", safe)
            safe = re.sub(r"https://[^\s<]+", lambda m: '<link href="'+m.group(0)+'">'+m.group(0)+'</link>', safe)
            story.append(Paragraph(safe, styles[style]))
    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#475569"))
        canvas.drawString(2*cm, 1.2*cm, "Pipeline de Dados com IoT e Docker")
        canvas.drawRightString(19*cm, 1.2*cm, str(doc.page))
    document = SimpleDocTemplate(str(output), pagesize=(21*cm,29.7*cm),
        leftMargin=2*cm,rightMargin=2*cm,topMargin=1.7*cm,bottomMargin=1.8*cm,
        title="Pipeline de Dados com IoT e Docker", author="")
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == "__main__":
    build()
