
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def process_csv_file(file_obj):
    try:
        df = pd.read_csv(file_obj)
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        if df.empty:
            raise ValueError("The CSV file is empty.")

        stats = {
            'total_count': int(len(df)),
            'avg_flowrate': float(df['Flowrate'].mean()),
            'avg_pressure': float(df['Pressure'].mean()),
            'avg_temperature': float(df['Temperature'].mean()),
            'type_distribution': df['Type'].value_counts().to_dict()
        }
        return stats
    except Exception as e:
        raise ValueError(str(e))

def generate_pdf_report(record):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"Chemical Equipment Report: {record.filename}", styles['Title']))
    elements.append(Spacer(1, 12))

    # Summary Text
    summary = record.summary_json
    elements.append(Paragraph(f"Generated on: {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [
        ["Parameter", "Value"],
        ["Total Equipment", summary['total_count']],
        ["Average Flowrate", f"{summary['avg_flowrate']:.2f} m3/h"],
        ["Average Pressure", f"{summary['avg_pressure']:.2f} bar"],
        ["Average Temperature", f"{summary['avg_temperature']:.2f} C"]
    ]

    t = Table(data, colWidths=[150, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.indigo),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 24))

    # Type Distribution
    elements.append(Paragraph("Equipment Type Distribution:", styles['Heading3']))
    dist_data = [["Type", "Count"]]
    for k, v in summary['type_distribution'].items():
        dist_data.append([k, v])
    
    dt = Table(dist_data, colWidths=[150, 150])
    dt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(dt)

    doc.build(elements)
    buffer.seek(0)
    return buffer
