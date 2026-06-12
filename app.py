from flask import Flask, render_template, request, jsonify
import database
import email_sender

app = Flask(__name__)

# Initialize database tables on start
database.init_db()

@app.route('/')
def index():
    return render_template('diagnostico_riesgos_garantis.html')

@app.route('/resultados')
def resultados():
    return render_template('resultados.html')

@app.route('/api/diagnosticos', methods=['GET'])
def get_diagnosticos():
    try:
        diagnosticos = database.get_diagnosticos()
        return jsonify(diagnosticos)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/diagnosticos', methods=['POST'])
def add_diagnostico():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        new_id = database.save_diagnostico(data)
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/diagnosticos/<int:diag_id>/contacto', methods=['PATCH'])
def patch_contacto(diag_id):
    try:
        data = request.json
        if not data or 'quiere_contacto' not in data:
            return jsonify({"success": False, "error": "Falta el campo quiere_contacto"}), 400
            
        quiere_contacto = data['quiere_contacto']
        database.update_contacto(diag_id, quiere_contacto)
        
        # Check SMTP config for automatic reports
        config = database.get_config_email()
        if config and config.get('enviar_automatico'):
            d = database.get_diagnostico_by_id(diag_id)
            if d:
                # Send report asynchronously or synchronously
                success, err = email_sender.send_email_report(config, d)
                if not success:
                    print(f"Error enviando correo automático: {err}")
                    
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/config-email', methods=['GET'])
def get_config_email():
    try:
        config = database.get_config_email()
        return jsonify(config)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/config-email', methods=['POST'])
def save_config_email():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        database.save_config_email(data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test-email', methods=['POST'])
def test_email():
    try:
        config = request.json
        if not config:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        # Create a mock diagnostic record for test purposes
        mock_diagnostic = {
            "nombre": "Usuario de Prueba",
            "cargo": "Director General",
            "empresa": "Garantis Test S.A.",
            "sector": "Servicios industriales",
            "email": config.get('destinatario', 'test@test.com'),
            "score": 68,
            "nivel": "MUY ALTO",
            "quiere_contacto": "Sí (Correo de prueba)",
            "riesgos": [
                "Incendio o explosión",
                "Responsabilidad civil ante terceros",
                "Pérdida de datos o ciberataque"
            ],
            "hallazgos": [
                {
                    "title": "Sin asesoría profesional continua",
                    "text": "Esta es una simulación del reporte enviado automáticamente al configurar tu servidor de correos.",
                    "type": "danger",
                    "icon": "ti-alert-circle"
                },
                {
                    "title": "Conexión SMTP exitosa",
                    "text": "Tu servidor SMTP está configurado correctamente y listo para despachar alertas de riesgo.",
                    "type": "success",
                    "icon": "ti-shield-check"
                }
            ]
        }
        
        success, err = email_sender.send_email_report(config, mock_diagnostic, is_test=True)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": err})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
