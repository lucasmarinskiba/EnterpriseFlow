def generate_invoice_pdf(client_name, subtotal, iva_rate, total, invoice_number, template):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, f"Factura {invoice_number}", ln=1, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Cliente: {client_name}", ln=1)
    pdf.cell(0, 10, f"Subtotal: ${subtotal:.2f}", ln=1)
    pdf.cell(0, 10, f"IVA: {int(iva_rate*100)}%", ln=1)
    pdf.cell(0, 10, f"Total: ${total:.2f}", ln=1)
    pdf.cell(0, 10, f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1)
    return pdf.output(dest='S').encode('latin1')

def send_invoice_email(client_email, invoice_number, total, pdf_bytes, message):
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email import encoders
    import smtplib
    msg = MIMEMultipart()
    msg['From'] = st.secrets["smtp"]["user"]
    msg['To'] = client_email
    msg['Subject'] = f"Factura {invoice_number}"

    body = f"{message}\nTotal: ${total:.2f}"
    msg.attach(MIMEText(body, 'plain'))
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename=Factura_{invoice_number}.pdf')
    msg.attach(part)

    with smtplib.SMTP(st.secrets["smtp"]["server"], st.secrets["smtp"]["port"]) as server:
        server.starttls()
        server.login(st.secrets["smtp"]["user"], st.secrets["smtp"]["password"])
        server.sendmail(st.secrets["smtp"]["user"], client_email, msg.as_string())
