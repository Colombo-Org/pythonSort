import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

# Função para criar as tabelas no banco de dados
def create_tables():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS vector_info (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT NOT NULL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS random_order (
                        id INTEGER PRIMARY KEY,
                        vector_id INTEGER,
                        order_index INTEGER,
                        value INTEGER,
                        FOREIGN KEY (vector_id) REFERENCES vector_info(id)
                    )''')
    conn.commit()
    conn.close()

# Executar a função para criar as tabelas
create_tables()

# Rotas Flask...
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
