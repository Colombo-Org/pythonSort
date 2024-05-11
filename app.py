from flask import Flask, jsonify, render_template
import random
import sqlite3
import time
import json


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


# Função para gerar um vetor ordenado e embaralhá-lo
def generate_shuffled_vector():
    ordered_vector = list(range(1, 50001))  # Gerar vetor ordenado
    random.shuffle(ordered_vector)  # Embaralhar o vetor
    return ordered_vector

# Função para salvar o vetor randomizado no banco de dados
def save_vector_to_database(vector):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Inserir o nome e a descrição do vetor na tabela vector_info
    cursor.execute('INSERT INTO vector_info (name, description) VALUES (?, ?)', ('shuffled_vector', 'Vetor embaralhado'))
    vector_id = cursor.lastrowid  # Obter o ID do vetor inserido

    vector_json = json.dumps(vector)

    # Inserir as ordens aleatórias na tabela random_order
    cursor.execute('INSERT INTO random_order (vector_id, value) VALUES (?, ?)', (vector_id, vector_json))
    conn.commit()
    conn.close()

# Função para realizar a tomada de tempo de 3 execuções
def measure_execution_time():
    times = []
    for _ in range(3):
        start_time = time.time()
        shuffled_vector = generate_shuffled_vector()
        times.append(time.time() - start_time)
    return times

def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        merge_sort(left_half)
        merge_sort(right_half)

        i = j = k = 0

        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1

# Rota para gerar o vetor randomizado e apresentar o resultado em JSON
@app.route('/random_vector')
def random_vector():
    shuffled_vector = generate_shuffled_vector()
    save_vector_to_database(shuffled_vector)
    execution_times = measure_execution_time()
    return jsonify({
        'shuffled_vector': shuffled_vector,
        'execution_times': execution_times
    })

@app.route('/sorted_vector')
def sorted_vector():
    
    merge_sorted = merge_sort()
    execution_times = measure_execution_time()
    return jsonify({
        'shuffled_vector': shuffled_vector,
        'execution_times': execution_times
    })

if __name__ == "__main__":
    app.run(debug=True)
