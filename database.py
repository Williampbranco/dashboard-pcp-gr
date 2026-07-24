import sqlite3

def inicializar_banco_dados():
    conn = sqlite3.connect("gr_cruzeiro_pcp.db")
    cursor = conn.cursor()

    # Tabela de Categorias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    """)

    # Tabela de Produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            categoria_id INTEGER,
            unidade_medida TEXT,
            densidade_g_ml REAL,
            estoque_atual REAL,
            estoque_minimo REAL,
            custo_unitario REAL,
            preco_venda_unitario REAL,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
    """)

    # Inserir Categorias Padrão (se não existirem)
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO categorias (nome) VALUES (?)", [
            ("Ácidos e Bases",),
            ("Saneantes Industrial",),
            ("Detergentes Concentrados",),
            ("Matérias-Primas Brutas",)
        ])

    # Inserir Produtos Padrão (se não existirem)
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        produtos_iniciais = [
            ("PROD001", "Ácido Clorídrico 32%", 1, "L", 1.16, 500, 2000, 3.50, 6.20),
            ("PROD002", "Hipoclorito de Sódio 12%", 1, "L", 1.20, 800, 2500, 1.80, 3.90),
            ("PROD003", "Ácido Sulfúrico 98%", 1, "L", 1.84, 300, 1500, 5.20, 9.80),
            ("PROD004", "Detergente Alcalino Clorado | GR 02", 2, "Kg", 1.10, 450, 1200, 4.10, 8.50),
            ("PROD005", "Barrilha Densa", 4, "Kg", 1.00, 200, 800, 2.90, 5.40),
            ("PROD006", "Soda Cústica Líquida 50%", 1, "L", 1.52, 3500, 2000, 4.80, 8.90),
            ("PROD007", "Detergente Neutro Concentrado", 3, "L", 1.02, 4000, 1500, 2.30, 5.10),
            ("PROD008", "Desinfetante Hospitalar 1%", 2, "L", 1.01, 2800, 1000, 3.10, 7.20),
            ("PROD009", "Ácido Nítrico 53%", 1, "L", 1.33, 1900, 1200, 6.40, 12.30),
            ("PROD0010", "Água Desmineralizada", 4, "L", 1.00, 8000, 3000, 0.40, 1.50)
        ]
        cursor.executemany("""
            INSERT INTO produtos (codigo, nome, categoria_id, unidade_medida, densidade_g_ml, estoque_atual, estoque_minimo, custo_unitario, preco_venda_unitario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, produtos_iniciais)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    inicializar_banco_dados()
    print("Banco de dados inicializado com sucesso!")