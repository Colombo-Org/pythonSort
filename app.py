from flask import Flask, jsonify, render_template, send_file
import random
import sqlite3
import time
import json
import matplotlib.pyplot as plt
from PIL import Image
import io

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


def generate_scatter_plot(x, y):
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, color='blue', marker='o', label='Scatter Plot')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Scatter Plot')
    plt.legend()
    
    # Salvar o gráfico em um arquivo
    plt.savefig('scatter_plot.png', format='png')

# Função para gerar um vetor ordenado e embaralhá-lo
def generate_shuffled_vector():
    shuffled_vector = random.sample(range(1, 1000000), 50000)  # Aqui usei um intervalo de 1 a 1.000.000, você pode ajustar conforme necessário
    return shuffled_vector

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
def measure_execution_time(function, *args):
    times = []
    for _ in range(3):
        start_time = time.time()
        shuffled_vector = function(*args)
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
        
        return arr 


# Rotas Flask...
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home(): 
    return render_template("home.html")

@app.route('/random_vector')
def random_vector():
    shuffled_vector = generate_shuffled_vector()
    save_vector_to_database(shuffled_vector)
    execution_times = measure_execution_time(generate_shuffled_vector)
    return jsonify({
        'shuffled_vector': shuffled_vector,
        'execution_times': execution_times
    })

@app.route('/sorted_vector')
def sorted_vector():
    # Consulta SQL para obter o último valor inserido na tabela random_order
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Consulta SQL para obter o último valor inserido na tabela random_order
    cursor.execute('SELECT value FROM random_order ORDER BY id DESC LIMIT 1')
    last_value = cursor.fetchone()[0]  # Obter o valor do primeiro campo do registro
    conn.close()
    
    # Remover os colchetes "[" e "]" e converter a string em uma lista de inteiros
    values = list(map(int, last_value.strip("[]").split(',')))

    # Chamar a função merge_sort para ordenar a lista
    merge_sorted = merge_sort(values)

    # Medir o tempo de execução
    execution_times = measure_execution_time(merge_sort, values)

    return jsonify({
        'sorted_vector': merge_sorted,
        'execution_times': execution_times
    })

@app.route('/scatter_plot')
def scatter_plot():
    # Suponha que você tenha seus próprios dados para o gráfico de dispersão
    x = [1, 2, 3, 4, 5]  # Dados x
    y = [10, 15, 20, 25, 30]  # Dados y

    # Gerar o gráfico de dispersão
    generate_scatter_plot(x, y)

    # Retorna os dados JSON
    data = {'x': x, 'y': y}
    return jsonify(data)

@app.route('/download_plot')
def download_plot():
    # Abre o gráfico gerado
    image_path = 'scatter_plot.png'
    return send_file(image_path, as_attachment=True, attachment_filename='scatter_plot.png')

if __name__ == "__main__":
    app.run(debug=True)
