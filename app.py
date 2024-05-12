from flask import Flask, jsonify, render_template, request, send_file
import random
import sqlite3
import time
import json
import matplotlib.pyplot as plt
import numpy as np


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


def generate_scatter_plot(data):

    np.random.seed(19680801)


    # Convertendo os dados de string para listas de números
    x_values = [float(x) for x in data["x"].split(",")]
    y_values = [float(y) for y in data["y"].split(",")]

    N = len(x_values)
    colors = np.random.rand(N)
    area = (30 * np.random.rand(N))**2  # 0 to 15 point radii

    plt.figure(figsize=(8, 6))
    plt.scatter(x_values, y_values, s=area, c=colors, marker='o', label='Scatter Plot')
    plt.xlabel(data["label_x"])
    plt.ylabel(data["label_y"])
    plt.title('Scatter Plot')
    plt.legend()
    
    # Salvar o gráfico em um arquivo
    plt.savefig('scatter_plot.png', format='png')

def generate_bar_chart(data):
    fig = plt.figure(figsize=(10, 5))

    x_values = [float(x) for x in data["x"].split(",")]
    y_values = [float(y) for y in data["y"].split(",")]

    N = len(x_values)
    colors = np.random.rand(N)

    # Criando o gráfico de barras
    plt.bar(x_values, y_values, color='blue', width=0.4)

    plt.xlabel(data["label_x"])
    plt.ylabel(data["label_y"])
    plt.title("Bar Chart")

    plt.savefig('bar_chart.png', format='png')

def generate_line_chart(data):
    fig = plt.figure(figsize=(10, 5))

    x_values = [float(x) for x in data["x"].split(",")]
    y_values = [float(y) for y in data["y"].split(",")]
    # Criando o gráfico de linha
    plt.plot(x_values, y_values, marker='o', color='blue', linestyle='-')

    plt.xlabel(data["label_x"])
    plt.ylabel(data["label_y"])
    plt.title("Line Chart")

    plt.savefig('line_chart.png', format='png')

def generate_bubble_chart(data):
    fig = plt.figure(figsize=(10, 5))

    x_values = [float(x) for x in data["x"].split(",")]
    y_values = [float(y) for y in data["y"].split(",")]
    
    # Criando o gráfico de dispersão com bolhas
    plt.scatter(x_values, y_values, s=100, alpha=0.5)

    plt.xlabel(data["label_x"])
    plt.ylabel(data["label_y"])
    plt.title("Bubble Chart")

    plt.savefig('bubble_chart.png', format='png')


def generate_dot_plot(data):
    fig = plt.figure(figsize=(10, 5))

    x_values = [float(x) for x in data["x"].split(",")]
    y_values = [float(y) for y in data["y"].split(",")]

    # Criando o gráfico de pontos
    plt.plot(x_values, y_values, marker='o', color="blue", linestyle='')

    plt.xlabel(data["label_x"])
    plt.ylabel(data["label_y"])
    plt.title("Dot Plot")

    plt.savefig('dot_plot.png', format='png')

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


# @app.route('/scatter_plot')
# def scatter_plot():
#     x = [1, 2, 3, 4, 5]  # Dados x
#     y = [10, 15, 20, 25, 30]  # Dados y

#     # Gerar o gráfico de dispersão
#     generate_scatter_plot(x,y)

#     image_path = 'bar_chart.png'
#     return send_file(image_path, as_attachment=True)

@app.route('/download_plot', methods=['POST'])
def download_plot():
    if request.method == 'POST':
        chart_type = request.form.get('chart_type')
        data = request.form.to_dict()

        # Mapeamento de tipos de gráfico para funções correspondentes
        chart_functions = {
            'scatter_plot': generate_scatter_plot,
            'line_chart': generate_line_chart,
            'bar_chart': generate_bar_chart,
            'bubble_chart': generate_bubble_chart,
            'dot_plot': generate_dot_plot,
        }

        # Verifica se o tipo de gráfico solicitado está no dicionário
        if chart_type in chart_functions:
            # Chama a função correspondente ao tipo de gráfico
            chart_functions[chart_type](data)

            image_path = f'{chart_type}.png'
            return send_file(image_path, as_attachment=True)
        else:
            return "Tipo de gráfico inválido", 400
    else:
        return "Método não permitido", 405
    
if __name__ == "__main__":
    app.run(debug=True)
