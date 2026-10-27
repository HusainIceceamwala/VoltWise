from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_report(bill_data, ai_result, score, status):

    doc = SimpleDocTemplate("VOLTWise_Report.pdf")

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("<b>VOLTWise AI Report</b>", styles["Title"]))

    elements.append(Paragraph("<br/>", styles["Normal"]))

    for key, value in bill_data.items():
        elements.append(
            Paragraph(f"<b>{key}</b> : {value}", styles["Normal"])
        )

    elements.append(Paragraph("<br/>", styles["Normal"]))

    elements.append(
        Paragraph(f"<b>Energy Score :</b> {score}/100", styles["Normal"])
    )

    elements.append(
        Paragraph(f"<b>Status :</b> {status}", styles["Normal"])
    )

    elements.append(Paragraph("<br/>", styles["Normal"]))

    elements.append(
        Paragraph("<b>AI Recommendation</b>", styles["Heading2"])
    )

    elements.append(
        Paragraph(ai_result.replace("\n", "<br/>"), styles["Normal"])
    )

    doc.build(elements)

    return "VOLTWise_Report.pdf"