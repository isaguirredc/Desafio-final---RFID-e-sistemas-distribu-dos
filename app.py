from flask import Flask, request, jsonify
import sqlite3
from pubsub import AsyncConn

app = Flask(__name__)
pubnub = AsyncConn("Flask Application", "microjobs")

USERNAME = "admin"
PASSWORD = "adminadmin"

def require_auth(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != USERNAME or auth.password !=PASSWORD:
            return jsonify({"error": "Acesso não autorizado"}), 401
        return f(*args, **kwargs)
    return decorated    

def connect_db():
    """Função para conectar ao banco de dados SQLite"""
    return sqlite3.connect('data.db')

def create_table():
    """Função para criar as tabelas no banco de dados"""
    conn = connect_db()
    cursor = conn.cursor()

    # tabela de registros gerais
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    )

    # tabela de funcionários
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )"""
    )

    # tabela de logs
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT CHECK(action IN ('ENTRADA', 'SAIDA')),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES funcionarios(id)
        )"""
    )

    conn.commit()
    conn.close()

def populate_funcionarios():
    """Função para adicionar funcionários iniciais caso a tabela esteja vazia"""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM funcionarios")
    count = cursor.fetchone()[0]

    if count == 0:
        funcionarios_iniciais = [
            ("Beltrano Silva",),
            ("Fulano Souza",),
            ("Fulaninho Lima",),
            ("Beltraninho Costa",)
        ]
        cursor.executemany("INSERT INTO funcionarios (nome) VALUES (?)", funcionarios_iniciais)
        conn.commit()

    conn.close()
# ========================= Inicializa Banco de Dados =========================
create_table()
populate_funcionarios()

@app.route('/', methods=['POST', 'GET'])
@require_auth
def use_api():
    try:
        # ====== POST ==========================================================================
        if request.method == "POST":
            data = request.json.get('data')  # Recebe o valor do corpo da requisição JSON
        
            if data is None:
                return jsonify({"error": "No value provided"}), 400
        
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO data (value) VALUES (?)', (data,))
                conn.commit()

            pubnub.publish({"text": data})
            
            return jsonify({"message": "Value added successfully"}), 201
        
        # ====== GET ==========================================================================
        elif request.method == "GET":
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM data')
                rows = cursor.fetchall()

            values = [{"id": row[0], "data": row[1]} for row in rows]

            return jsonify(values), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================= API para Registro de Acessos =========================
@app.route('/acesso', methods=['POST'])
def registrar_acesso():
    """Registra uma entrada ou saída de um funcionário"""
    try:
        user_id = request.json.get("user_id")
        action = request.json.get("action")  # "ENTRADA" ou "SAIDA"

        if not user_id or action not in ["ENTRADA", "SAIDA"]:
            return jsonify({"error": "Parâmetros inválidos"}), 400

        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (user_id, action))
            conn.commit()

        return jsonify({"message": "Acesso registrado com sucesso!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================= Iniciar o Servidor =========================
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)