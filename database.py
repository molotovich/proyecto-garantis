import sqlite3
import json
import os

DB_PATH = 'garantis_diagnosticos.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create diagnosticos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diagnosticos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            nombre TEXT NOT NULL,
            cargo TEXT NOT NULL,
            empresa TEXT NOT NULL,
            sector TEXT NOT NULL,
            email TEXT,
            score INTEGER NOT NULL,
            nivel TEXT NOT NULL,
            riesgos TEXT,
            hallazgos TEXT,
            quiere_contacto TEXT DEFAULT 'Pendiente'
        )
    ''')
    
    # Create email settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracion_email (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            smtp_host TEXT,
            smtp_port INTEGER,
            smtp_user TEXT,
            smtp_password TEXT,
            smtp_use_tls INTEGER DEFAULT 1,
            smtp_use_ssl INTEGER DEFAULT 0,
            remitente TEXT,
            destinatario TEXT,
            enviar_automatico INTEGER DEFAULT 0
        )
    ''')
    
    # Initialize default config if not exists
    cursor.execute('SELECT COUNT(*) FROM configuracion_email WHERE id = 1')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO configuracion_email (
                id, smtp_host, smtp_port, smtp_user, smtp_password, 
                smtp_use_tls, smtp_use_ssl, remitente, destinatario, enviar_automatico
            ) VALUES (1, '', 587, '', '', 1, 0, '', '', 0)
        ''')
        
    conn.commit()
    conn.close()

def save_diagnostico(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert lists/dicts to JSON strings
    riesgos_json = json.dumps(data.get('riesgos', []))
    hallazgos_json = json.dumps(data.get('hallazgos', []))
    
    cursor.execute('''
        INSERT INTO diagnosticos (
            nombre, cargo, empresa, sector, email, score, nivel, riesgos, hallazgos, quiere_contacto
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('nombre'),
        data.get('cargo'),
        data.get('empresa'),
        data.get('sector'),
        data.get('email', ''),
        data.get('score'),
        data.get('nivel'),
        riesgos_json,
        hallazgos_json,
        data.get('quiere_contacto', 'Pendiente')
    ))
    
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_contacto(diagnostico_id, quiere_contacto):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE diagnosticos 
        SET quiere_contacto = ? 
        WHERE id = ?
    ''', (quiere_contacto, diagnostico_id))
    conn.commit()
    conn.close()

def get_diagnosticos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM diagnosticos ORDER BY fecha DESC')
    rows = cursor.fetchall()
    conn.close()
    
    diagnosticos = []
    for r in rows:
        d = dict(r)
        # Parse JSON lists back
        try:
            d['riesgos'] = json.loads(d['riesgos'])
        except Exception:
            d['riesgos'] = []
        try:
            d['hallazgos'] = json.loads(d['hallazgos'])
        except Exception:
            d['hallazgos'] = []
        diagnosticos.append(d)
        
    return diagnosticos

def get_diagnostico_by_id(diagnostico_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM diagnosticos WHERE id = ?', (diagnostico_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    d = dict(row)
    try:
        d['riesgos'] = json.loads(d['riesgos'])
    except Exception:
        d['riesgos'] = []
    try:
        d['hallazgos'] = json.loads(d['hallazgos'])
    except Exception:
        d['hallazgos'] = []
    return d

def get_config_email():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM configuracion_email WHERE id = 1')
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_config_email(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE configuracion_email SET
            smtp_host = ?,
            smtp_port = ?,
            smtp_user = ?,
            smtp_password = ?,
            smtp_use_tls = ?,
            smtp_use_ssl = ?,
            remitente = ?,
            destinatario = ?,
            enviar_automatico = ?
        WHERE id = 1
    ''', (
        data.get('smtp_host', ''),
        int(data.get('smtp_port', 587)),
        data.get('smtp_user', ''),
        data.get('smtp_password', ''),
        1 if data.get('smtp_use_tls') else 0,
        1 if data.get('smtp_use_ssl') else 0,
        data.get('remitente', ''),
        data.get('destinatario', ''),
        1 if data.get('enviar_automatico') else 0
    ))
    conn.commit()
    conn.close()
