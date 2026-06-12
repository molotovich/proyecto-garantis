import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_report(config, d, is_test=False):
    # Ensure config has the required values
    smtp_host = config.get('smtp_host')
    smtp_port = config.get('smtp_port')
    smtp_user = config.get('smtp_user')
    smtp_pass = config.get('smtp_password')
    remitente = config.get('remitente')
    destinatario = config.get('destinatario')
    
    if not smtp_host or not destinatario:
        return False, "Host SMTP o destinatario no configurados."
        
    # Set default values if empty
    if not remitente:
        remitente = smtp_user or "noreply@garantis.mx"

    # Define risk colors based on level
    nivel = d.get('nivel', 'BAJO').upper()
    level_colors = {
        'CRÍTICO': {'bg': '#fdf0f0', 'text': '#c0392b', 'label': '#5a1a1a'},
        'MUY ALTO': {'bg': '#fdf0f0', 'text': '#e74c3c', 'label': '#5a1a1a'},
        'ALTO': {'bg': '#fffbea', 'text': '#d68910', 'label': '#5a4000'},
        'MEDIO': {'bg': '#fffde0', 'text': '#b7950b', 'label': '#5a4400'},
        'BAJO': {'bg': '#eaf5ee', 'text': '#1e8449', 'label': '#1a4a2a'}
    }
    colors = level_colors.get(nivel, level_colors['BAJO'])

    # Compile findings HTML list
    findings_html = ""
    for f in d.get('hallazgos', []):
        f_type = f.get('type', 'warning')
        card_colors = {
            'danger': {'bg': '#fdf0f0', 'border': '#f0b0b0', 'text': '#5a1a1a'},
            'warning': {'bg': '#fffbea', 'border': '#f0d070', 'text': '#5a4000'},
            'success': {'bg': '#eaf5ee', 'border': '#90d0a0', 'text': '#1a4a2a'}
        }
        cc = card_colors.get(f_type, card_colors['warning'])
        
        findings_html += f"""
        <div style="background-color: {cc['bg']}; border: 1px solid {cc['border']}; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; color: {cc['text']}; font-family: sans-serif;">
            <strong style="display: block; font-size: 14px; margin-bottom: 4px;">{f.get('title')}</strong>
            <span style="font-size: 13px; line-height: 1.4;">{f.get('text')}</span>
        </div>
        """

    # Compile risks HTML list
    risks_html = ""
    for r in d.get('riesgos', []):
        risks_html += f"""
        <span style="display: inline-block; background-color: #d6eaf8; color: #1a3a5c; border: 1px solid #a8ccea; border-radius: 20px; padding: 4px 12px; font-size: 12px; font-weight: 600; margin: 4px; font-family: sans-serif;">
            {r}
        </span>
        """
    if not risks_html:
        risks_html = '<span style="font-size: 13px; color: #6b7a8d; font-family: sans-serif;">Ninguno especificado</span>'

    # Subject line
    prefix = "[PRUEBA] " if is_test else ""
    subject = f"{prefix}Nuevo Diagnóstico de Riesgos: {d.get('empresa')} ({d.get('nivel')})"

    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = remitente
    msg['To'] = destinatario

    # HTML Body Template
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="background-color: #f4f7fb; padding: 20px; font-family: sans-serif; color: #2b2d42;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid #d0dce8;">
            <!-- Brand Header -->
            <div style="background: linear-gradient(135deg, #1a3a5c 0%, #2a7fc1 55%, #6b3fa0 100%); padding: 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 800; letter-spacing: 2px;">GARANTIS</h1>
                <div style="color: rgba(255,255,255,0.8); font-size: 12px; letter-spacing: 1.5px; margin-top: 5px;">DIAGNÓSTICO DE RIESGOS EMPRESARIALES</div>
            </div>
            
            <!-- Summary Info -->
            <div style="padding: 24px 30px;">
                <div style="text-align: center; margin-bottom: 25px;">
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 1.5px; color: #6b7a8d; margin-bottom: 5px;">Nivel de Exposición Estimado</div>
                    <div style="font-size: 54px; font-weight: 800; color: {colors['text']}; line-height: 1; margin-bottom: 8px;">{d.get('score')}%</div>
                    <div style="display: inline-block; background-color: {colors['bg']}; color: {colors['label']}; border-radius: 20px; padding: 6px 20px; font-weight: 700; font-size: 12px; letter-spacing: 1px; text-transform: uppercase;">
                        {d.get('nivel')}
                    </div>
                </div>

                <!-- User Details Table -->
                <div style="border-top: 1px solid #eaf1f8; padding-top: 20px; margin-bottom: 25px;">
                    <h3 style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #6b7a8d; margin-top: 0; margin-bottom: 15px;">Información del Negocio</h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr>
                            <td style="padding: 6px 0; color: #6b7a8d; width: 35%;"><strong>Nombre:</strong></td>
                            <td style="padding: 6px 0; color: #2b2d42;">{d.get('nombre')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #6b7a8d;"><strong>Empresa:</strong></td>
                            <td style="padding: 6px 0; color: #2b2d42;">{d.get('empresa')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #6b7a8d;"><strong>Cargo/Rol:</strong></td>
                            <td style="padding: 6px 0; color: #2b2d42;">{d.get('cargo')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #6b7a8d;"><strong>Sector:</strong></td>
                            <td style="padding: 6px 0; color: #2b2d42;">{d.get('sector')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #6b7a8d;"><strong>Correo:</strong></td>
                            <td style="padding: 6px 0; color: #2b2d42;">{d.get('email') or 'No proporcionado'}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #6b7a8d;"><strong>Contacto Solicitado:</strong></td>
                            <td style="padding: 6px 0; color: #2b2d42; font-weight: bold;">{d.get('quiere_contacto')}</td>
                        </tr>
                    </table>
                </div>

                <!-- Risks -->
                <div style="border-top: 1px solid #eaf1f8; padding-top: 20px; margin-bottom: 25px;">
                    <h3 style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #6b7a8d; margin-top: 0; margin-bottom: 12px;">Riesgos Identificados</h3>
                    <div style="margin: -4px;">
                        {risks_html}
                    </div>
                </div>

                <!-- Findings -->
                <div style="border-top: 1px solid #eaf1f8; padding-top: 20px;">
                    <h3 style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #6b7a8d; margin-top: 0; margin-bottom: 15px;">Principales Hallazgos</h3>
                    <div>
                        {findings_html}
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f4f7fb; border-top: 1px solid #eaf1f8; padding: 20px; text-align: center; font-size: 11px; color: #6b7a8d;">
                Este correo fue enviado de forma automática por la herramienta de diagnóstico de <strong>Garantis Asesores en Seguros</strong>.<br>
                Configura los ajustes de recepción en el panel administrativo de la aplicación.
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, 'html'))

    try:
        # Determine encryption type and connect
        if config.get('smtp_use_ssl'):
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            if config.get('smtp_use_tls'):
                server.starttls()
                
        # Authenticate if login details are provided
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
            
        # Send mail
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)
