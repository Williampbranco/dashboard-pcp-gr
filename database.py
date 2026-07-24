import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def inicializar_banco_dados(db_name="gr_cruzeiro_pcp.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 1. TABELA DE CATEGORIAS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)

    # 2. TABELA DE PRODUTOS / INSUMOS (Mestre de Materiais)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nome TEXT NOT NULL,
        categoria_id INTEGER,
        tipo TEXT CHECK(tipo IN ('Acabado', 'Materia-Prima', 'Embalagem')),
        unidade_medida TEXT DEFAULT 'kg',
        densidade_g_ml REAL DEFAULT 1.0,
        validade_dias INTEGER DEFAULT 365,
        estoque_minimo REAL DEFAULT 500.0,
        estoque_atual REAL DEFAULT 1000.0,
        custo_unitario REAL DEFAULT 0.0,
        preco_venda_unitario REAL DEFAULT 0.0,
        FOREIGN KEY (categoria_id) REFERENCES categorias (id)
    )
    """)

    # 3. TABELA DE LINHAS DE PRODUÇÃO / ENVASE (RCCP)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS linhas_producao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        capacidade_nominal_lh REAL,
        horas_disponiveis_dia REAL DEFAULT 16.0,
        tipo_envase TEXT
    )
    """)

    # 4. TABELA DE BOMS / FICHAS TÉCNICAS (MRP)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estruturas_bom (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_pai_id INTEGER,
        insumo_filho_id INTEGER,
        quantidade_por_unidade REAL,
        FOREIGN KEY (produto_pai_id) REFERENCES produtos (id),
        FOREIGN KEY (insumo_filho_id) REFERENCES produtos (id)
    )
    """)

    # 5. TABELA DE ORDENS DE PRODUÇÃO (OP)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ordens_producao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_op TEXT UNIQUE,
        produto_id INTEGER,
        quantidade_planejada REAL,
        linha_id INTEGER,
        data_emissao DATE,
        data_previsao DATE,
        status TEXT DEFAULT 'PLANEJADA' CHECK(status IN ('PLANEJADA', 'EM_PROCESSO', 'CONCLUIDA', 'CANCELADA')),
        FOREIGN KEY (produto_id) REFERENCES produtos (id),
        FOREIGN KEY (linha_id) REFERENCES linhas_producao (id)
    )
    """)

    conn.commit()

    # --- POPULANDO DADOS INICIAIS DA GR CRUZEIRO ---

    # Inserir Categorias
    cats = [
        "Ácidos", "Sais e Inorgânicos", "Bases e Álcalis", "Detergentes e Sanitizantes",
        "Tratamento de Água / Polímeros", "Linha GR Especialidades", "Peróxidos e Oxidantes", "Solventes e Outros"
    ]
    for c in cats:
        cursor.execute("INSERT OR IGNORE INTO categorias (nome) VALUES (?)", (c,))

    # Inserir Linhas de Envase Padrão
    linhas = [
        ("Linha 01 - Envase Fracionado (Bombonas 20L)", 1200.0, 16.0, "Pequenos Volumes"),
        ("Linha 02 - Envase Granel (Tambores e IBCs)", 4500.0, 16.0, "Grandes Volumes"),
        ("Linha 03 - Mistura e Reatores de Ácidos", 2500.0, 20.0, "Formulação Líquida"),
        ("Linha 04 - Envasadora de Pós e Granulados", 1000.0, 12.0, "Sólidos")
    ]
    for l in linhas:
        cursor.execute("INSERT OR IGNORE INTO linhas_producao (nome, capacidade_nominal_lh, horas_disponiveis_dia, tipo_envase) VALUES (?,?,?,?)", l)

    # LISTA COMPLETA DE PRODUTOS DA GR CRUZEIRO
    produtos_gr = [
        ("Ácido Acético Glacial", "Ácidos", "kg", 1.05, 365, 2000, 5000, 8.50, 14.20),
        ("Ácido Acrílico", "Ácidos", "kg", 1.05, 180, 1000, 2500, 12.00, 19.50),
        ("Ácido Adípico", "Ácidos", "kg", 1.36, 365, 500, 1200, 15.00, 24.00),
        ("Ácido Bórico", "Ácidos", "kg", 1.43, 720, 1000, 3000, 9.20, 15.00),
        ("Ácido Cítrico Anidro", "Ácidos", "kg", 1.66, 720, 2000, 6000, 11.00, 17.50),
        ("Ácido Cítrico Solução 40%", "Ácidos", "L", 1.18, 365, 3000, 8000, 5.20, 9.10),
        ("Ácido Cítrico Solução 50%", "Ácidos", "L", 1.23, 365, 3000, 7500, 6.10, 10.80),
        ("Ácido Clorídrico 32%", "Ácidos", "L", 1.16, 365, 5000, 15000, 2.80, 5.50),
        ("Ácido Clorídrico 32% Com metais pesados", "Ácidos", "L", 1.16, 365, 2000, 4000, 2.10, 4.20),
        ("Ácido Fluossilícico", "Ácidos", "L", 1.31, 365, 1000, 2000, 7.80, 13.00),
        ("Ácido Fórmico 85%", "Ácidos", "kg", 1.22, 365, 1500, 3500, 8.90, 14.80),
        ("Ácido Fosfórico 70%", "Ácidos", "kg", 1.53, 365, 2000, 5000, 9.50, 16.00),
        ("Ácido Fosfórico 85%", "Ácidos", "kg", 1.68, 365, 3000, 9000, 11.80, 19.20),
        ("Ácido Lático 85%", "Ácidos", "kg", 1.21, 365, 1000, 2200, 13.50, 21.00),
        ("Ácido Nítrico 53%", "Ácidos", "L", 1.33, 365, 4000, 12000, 3.40, 6.80),
        ("Ácido Oxálico", "Ácidos", "kg", 1.90, 720, 800, 1500, 10.20, 17.00),
        ("Ácido Peracético 15%", "Peróxidos e Oxidantes", "L", 1.12, 180, 1500, 4000, 11.50, 18.50),
        ("Ácido Peracético 5%", "Peróxidos e Oxidantes", "L", 1.04, 180, 1000, 3000, 5.20, 9.80),
        ("Ácido Sulfônico 90%", "Detergentes e Sanitizantes", "kg", 1.06, 365, 3000, 8500, 9.80, 15.90),
        ("Ácido Sulfúrico 25%", "Ácidos", "L", 1.18, 720, 2000, 5000, 1.80, 3.50),
        ("Ácido Sulfúrico 30%", "Ácidos", "L", 1.22, 720, 2000, 5000, 2.10, 4.00),
        ("Ácido Sulfúrico 35%", "Ácidos", "L", 1.26, 720, 2000, 5000, 2.40, 4.50),
        ("Ácido Sulfúrico 40%", "Ácidos", "L", 1.30, 720, 2000, 5000, 2.70, 5.00),
        ("Ácido Sulfúrico 50%", "Ácidos", "L", 1.40, 720, 3000, 7000, 3.20, 6.10),
        ("Ácido Sulfúrico 60%", "Ácidos", "L", 1.50, 720, 3000, 7000, 3.80, 7.00),
        ("Ácido Sulfúrico 75%", "Ácidos", "L", 1.67, 720, 4000, 10000, 4.50, 8.20),
        ("Ácido Sulfúrico 78%", "Ácidos", "L", 1.71, 720, 4000, 10000, 4.80, 8.80),
        ("Ácido Sulfúrico 98%", "Ácidos", "L", 1.84, 720, 5000, 18000, 5.50, 10.20),
        ("Ácido Tricloroisocianúrico", "Peróxidos e Oxidantes", "kg", 2.19, 365, 1000, 2000, 18.00, 29.00),
        ("Ácido Tricloroisocianurico Granulado", "Peróxidos e Oxidantes", "kg", 2.19, 365, 1000, 2500, 19.00, 31.00),
        ("Ácido Tricloroisocianurico Tabletes", "Peróxidos e Oxidantes", "kg", 2.19, 365, 1000, 3000, 21.00, 34.00),
        ("Aluminato de Sódio 13%", "Tratamento de Água / Polímeros", "L", 1.25, 180, 2000, 6000, 3.10, 5.80),
        ("Aluminato de Sódio 20%", "Tratamento de Água / Polímeros", "L", 1.35, 180, 2000, 5000, 4.20, 7.50),
        ("Amida 60%", "Detergentes e Sanitizantes", "kg", 1.00, 365, 800, 2000, 12.50, 20.00),
        ("Amida 80%", "Detergentes e Sanitizantes", "kg", 1.00, 365, 1000, 2500, 15.00, 24.50),
        ("Amônia", "Bases e Álcalis", "kg", 0.73, 365, 2000, 4000, 6.00, 11.00),
        ("Antiespumante à base de água", "Linha GR Especialidades", "kg", 1.00, 180, 500, 1200, 14.00, 23.00),
        ("Antiespumante à base de óleo", "Linha GR Especialidades", "kg", 0.92, 180, 500, 1000, 18.00, 29.00),
        ("Antiespumante à base de silicone", "Linha GR Especialidades", "kg", 1.01, 365, 500, 1500, 22.00, 36.00),
        ("Barrilha Densa", "Sais e Inorgânicos", "kg", 2.53, 720, 3000, 10000, 2.50, 4.80),
        ("Barrilha Leve", "Sais e Inorgânicos", "kg", 2.53, 720, 3000, 10000, 2.40, 4.60),
        ("Benzoato de Sódio", "Sais e Inorgânicos", "kg", 1.44, 720, 500, 1500, 16.00, 26.00),
        ("Bicarbonato de Sódio", "Sais e Inorgânicos", "kg", 2.20, 720, 2000, 8000, 3.20, 5.90),
        ("Bissulfito de Sódio 30%", "Sais e Inorgânicos", "L", 1.30, 180, 2000, 6000, 2.80, 5.20),
        ("Bissulfito de Sódio 37%", "Sais e Inorgânicos", "L", 1.35, 180, 2000, 6000, 3.30, 6.00),
        ("Bissulfito de Sódio 40%", "Sais e Inorgânicos", "L", 1.38, 180, 2000, 6000, 3.60, 6.60),
        ("Borax Decahidratado", "Sais e Inorgânicos", "kg", 1.73, 720, 1000, 3000, 7.50, 12.80),
        ("Cal Hidratada", "Bases e Álcalis", "kg", 2.21, 365, 5000, 15000, 0.80, 1.80),
        ("Cal Hidratada – Solução", "Bases e Álcalis", "L", 1.15, 90, 2000, 5000, 1.20, 2.50),
        ("Cal Virgem", "Bases e Álcalis", "kg", 3.34, 180, 5000, 12000, 0.95, 2.10),
        ("Carbonato de Cálcio Precipitado", "Sais e Inorgânicos", "kg", 2.71, 720, 2000, 6000, 1.50, 3.20),
        ("Carbonato de Sódio – Barrilha Densa", "Sais e Inorgânicos", "kg", 2.53, 720, 2000, 5000, 2.50, 4.80),
        ("Carbonato de Sódio – Barrilha Leve", "Sais e Inorgânicos", "kg", 2.53, 720, 2000, 5000, 2.40, 4.60),
        ("Carbonato de Sódio – Solução 20%", "Sais e Inorgânicos", "L", 1.20, 180, 1000, 3000, 1.80, 3.60),
        ("Carbonato de Sódio – Solução 6% a 7%", "Sais e Inorgânicos", "L", 1.06, 180, 1000, 3000, 0.90, 2.10),
        ("Carvão Ativado", "Tratamento de Água / Polímeros", "kg", 0.50, 1080, 1000, 4000, 12.00, 21.00),
        ("Citrato de Sódio", "Sais e Inorgânicos", "kg", 1.70, 720, 1000, 2500, 10.50, 17.20),
        ("Cloreto de Benzalconio", "Detergentes e Sanitizantes", "kg", 0.98, 365, 500, 1500, 24.00, 39.00),
        ("Cloreto de Cálcio 40%", "Sais e Inorgânicos", "L", 1.40, 365, 2000, 6000, 2.20, 4.30),
        ("Cloreto de Cálcio Di-Hidratado", "Sais e Inorgânicos", "kg", 1.85, 365, 1000, 4000, 3.50, 6.80),
        ("Cloreto de Metileno", "Solventes e Outros", "kg", 1.33, 365, 1000, 2000, 14.20, 23.00),
        ("Cloreto Férrico", "Tratamento de Água / Polímeros", "L", 1.42, 365, 3000, 9000, 3.80, 7.20),
        ("Cloridrato de Alumínio", "Tratamento de Água / Polímeros", "L", 1.33, 365, 2000, 6000, 4.50, 8.50),
        ("Clorito de Sódio 80%", "Peróxidos e Oxidantes", "kg", 2.50, 365, 500, 1500, 28.00, 45.00),
        ("Cloro gás", "Peróxidos e Oxidantes", "kg", 3.20, 365, 1000, 3000, 6.50, 12.00),
        ("Detergentes e Sanitizantes | GR 02 (Alcalino Clorado)", "Detergentes e Sanitizantes", "L", 1.10, 180, 1000, 3500, 4.20, 8.50),
        ("Detergentes e Sanitizantes | GR 04 (Desengordurante)", "Detergentes e Sanitizantes", "L", 1.05, 180, 1000, 3000, 5.10, 9.90),
        ("Detergentes e Sanitizantes | GR 01 (Neutro)", "Detergentes e Sanitizantes", "L", 1.02, 180, 1500, 4000, 3.20, 6.80),
        ("Detergentes e Sanitizantes | GR 03 (Premium)", "Detergentes e Sanitizantes", "L", 1.04, 180, 1000, 2800, 6.50, 12.20),
        ("Dicloroisocianurato de Sódio 60% – Granulado", "Peróxidos e Oxidantes", "kg", 0.95, 365, 800, 2000, 22.00, 36.00),
        ("EDTA", "Sais e Inorgânicos", "kg", 0.86, 720, 500, 1500, 19.50, 32.00),
        ("Enxofre", "Sais e Inorgânicos", "kg", 2.07, 1080, 2000, 5000, 3.10, 6.00),
        ("Fluorsilicato de Sódio", "Sais e Inorgânicos", "kg", 2.68, 365, 500, 1200, 8.90, 15.00),
        ("Formol", "Solventes e Outros", "L", 1.09, 180, 2000, 5000, 4.10, 7.80),
        ("Fosfato Diamônico (DAP)", "Sais e Inorgânicos", "kg", 1.62, 720, 1000, 4000, 5.80, 10.50),
        ("Fosfato Monoamônio (MAP)", "Sais e Inorgânicos", "kg", 1.80, 720, 1000, 4000, 6.20, 11.20),
        ("Fosfato Monossódico", "Sais e Inorgânicos", "kg", 2.36, 720, 1000, 3000, 7.10, 12.50),
        ("Glicerina", "Solventes e Outros", "kg", 1.26, 365, 2000, 6000, 6.80, 11.90),
        ("Gluconato de Sódio", "Sais e Inorgânicos", "kg", 1.50, 720, 500, 1500, 12.00, 20.00),
        ("Goma Xantana", "Linha GR Especialidades", "kg", 1.50, 720, 300, 800, 38.00, 62.00),
        ("GR AD Alcalino Plus", "Linha GR Especialidades", "L", 1.12, 180, 500, 1500, 8.50, 16.00),
        ("GR AD05", "Linha GR Especialidades", "L", 1.05, 180, 500, 1200, 9.20, 17.50),
        ("GR BIO-X 200", "Linha GR Especialidades", "L", 1.02, 180, 300, 900, 18.00, 32.00),
        ("GR BIO-X 300", "Linha GR Especialidades", "L", 1.02, 180, 300, 900, 22.00, 39.00),
        ("GR Bioact", "Linha GR Especialidades", "L", 1.03, 180, 400, 1000, 15.50, 28.00),
        ("GR Bleach 100", "Linha GR Especialidades", "L", 1.15, 180, 1000, 2500, 6.80, 12.50),
        ("GR Clean", "Linha GR Especialidades", "L", 1.04, 180, 1000, 3000, 5.50, 10.50),
        ("GR Cloud Buster 6100", "Linha GR Especialidades", "L", 1.08, 180, 300, 800, 25.00, 44.00),
        ("GR Cloud Buster 6200", "Linha GR Especialidades", "L", 1.08, 180, 300, 800, 27.00, 48.00),
        ("GR Cloud Buster 6300", "Linha GR Especialidades", "L", 1.09, 180, 300, 800, 29.00, 52.00),
        ("GR Coalter YKR12", "Linha GR Especialidades", "kg", 1.15, 365, 200, 600, 42.00, 75.00),
        ("GR Decolor Floc 51", "Tratamento de Água / Polímeros", "L", 1.18, 180, 1000, 2500, 11.00, 20.00),
        ("GR Delamix 580", "Linha GR Especialidades", "kg", 1.10, 180, 300, 800, 19.00, 34.00),
        ("GR DSP HC 601", "Linha GR Especialidades", "L", 1.06, 180, 200, 500, 31.00, 55.00),
        ("GR DSP Lowfix 201", "Linha GR Especialidades", "L", 1.05, 180, 200, 500, 28.00, 49.00),
        ("GR DSP Vest 001", "Linha GR Especialidades", "L", 1.04, 180, 200, 500, 26.00, 46.00),
        ("GR Floc RX 50", "Tratamento de Água / Polímeros", "kg", 1.00, 365, 500, 1200, 35.00, 60.00),
        ("GR Flow RD 600", "Linha GR Especialidades", "L", 1.02, 180, 300, 800, 17.00, 30.00),
        ("GR Flow RD 750", "Linha GR Especialidades", "L", 1.03, 180, 300, 800, 19.50, 35.00),
        ("GR G-FIX 420", "Linha GR Especialidades", "kg", 1.12, 180, 200, 500, 33.00, 58.00),
        ("GR Map Coalter KM14", "Linha GR Especialidades", "kg", 1.20, 365, 200, 500, 45.00, 80.00),
        ("GR Ortophos 5000", "Tratamento de Água / Polímeros", "L", 1.25, 365, 500, 1500, 14.00, 25.00),
        ("GR Pet Soap-255", "Detergentes e Sanitizantes", "L", 1.02, 180, 500, 1500, 7.80, 14.50),
        ("GR Poli Aniônico – Emulsão", "Tratamento de Água / Polímeros", "kg", 1.05, 180, 1000, 3000, 22.00, 38.00),
        ("GR Poli Aniônico – Granulado", "Tratamento de Água / Polímeros", "kg", 0.80, 365, 1000, 3000, 25.00, 42.00),
        ("GR Poli Catiônico – Emulsão", "Tratamento de Água / Polímeros", "kg", 1.05, 180, 1000, 3000, 24.00, 41.00),
        ("GR Poli Catiônico – Granulado", "Tratamento de Água / Polímeros", "kg", 0.80, 365, 1000, 3000, 28.00, 48.00),
        ("GR Poli Não-Iônico – Emulsão", "Tratamento de Água / Polímeros", "kg", 1.05, 180, 500, 1500, 23.00, 40.00),
        ("GR Release YKR", "Linha GR Especialidades", "kg", 0.95, 180, 200, 500, 39.00, 68.00),
        ("GR Thermal Fluid", "Linha GR Especialidades", "L", 0.98, 365, 500, 1500, 21.00, 37.00),
        ("GR TNN", "Linha GR Especialidades", "L", 1.04, 180, 300, 800, 16.00, 29.00),
        ("GR Trifluor", "Linha GR Especialidades", "L", 1.15, 180, 200, 500, 48.00, 85.00),
        ("GR WR 812", "Linha GR Especialidades", "L", 1.02, 180, 300, 800, 18.50, 33.00),
        ("Hexametafosfato de Sódio", "Sais e Inorgânicos", "kg", 2.33, 720, 1000, 3000, 11.50, 19.00),
        ("Hidrossulfito de Sódio 88%", "Sais e Inorgânicos", "kg", 2.19, 180, 1000, 2500, 14.00, 24.00),
        ("Hidróxido de Alumínio", "Bases e Álcalis", "kg", 2.42, 720, 2000, 6000, 4.20, 8.00),
        ("Hidróxido de Amônio 25%", "Bases e Álcalis", "L", 0.91, 180, 2000, 5000, 2.90, 5.50),
        ("Hidróxido de Amônio 28%", "Bases e Álcalis", "L", 0.90, 180, 2000, 5000, 3.20, 6.10),
        ("Hidróxido de Potássio – Em escamas", "Bases e Álcalis", "kg", 2.04, 365, 1500, 4000, 10.50, 18.00),
        ("Hidróxido de Potássio – Em pó", "Bases e Álcalis", "kg", 2.04, 365, 1000, 3000, 11.20, 19.50),
        ("Hidróxido de Potássio – Solução", "Bases e Álcalis", "L", 1.45, 365, 2000, 6000, 6.80, 12.00),
        ("Hidróxido de Sódio 20%", "Bases e Álcalis", "L", 1.22, 365, 3000, 8000, 1.90, 3.80),
        ("Hidróxido de Sódio 25%", "Bases e Álcalis", "L", 1.27, 365, 3000, 8000, 2.30, 4.50),
        ("Hidróxido de Sódio 30%", "Bases e Álcalis", "L", 1.33, 365, 4000, 10000, 2.70, 5.20),
        ("Hidróxido de Sódio 32%", "Bases e Álcalis", "L", 1.35, 365, 4000, 10000, 2.90, 5.60),
        ("Hidróxido de Sódio 50%", "Bases e Álcalis", "L", 1.52, 365, 5000, 15000, 3.80, 7.20),
        ("Hipoclorito de Cálcio 65% – Granulado", "Peróxidos e Oxidantes", "kg", 2.35, 365, 1000, 3000, 15.00, 26.00),
        ("Hipoclorito de Cálcio 65% – Tablete", "Peróxidos e Oxidantes", "kg", 2.35, 365, 1000, 3000, 17.00, 29.50),
        ("Hipoclorito de Sódio 10%", "Peróxidos e Oxidantes", "L", 1.15, 60, 3000, 8000, 1.20, 2.80),
        ("Hipoclorito de Sódio 12%", "Peróxidos e Oxidantes", "L", 1.20, 60, 4000, 12000, 1.40, 3.20),
        ("Hipoclorito de Sódio 13%", "Peróxidos e Oxidantes", "L", 1.22, 60, 4000, 10000, 1.60, 3.60),
        ("Lauril 27% | Éter Sulfato de Sódio", "Detergentes e Sanitizantes", "kg", 1.05, 365, 2000, 6000, 5.20, 9.50),
        ("Lauril 70% | Éter Sulfato de Sódio", "Detergentes e Sanitizantes", "kg", 1.08, 365, 2000, 5000, 11.50, 19.80),
        ("Metabissulfito de Sódio", "Sais e Inorgânicos", "kg", 1.48, 365, 1000, 4000, 4.80, 8.90),
        ("Metassilicato de Sódio", "Sais e Inorgânicos", "kg", 2.40, 365, 1000, 3000, 5.50, 10.00),
        ("Molibdato de Sódio 39%", "Sais e Inorgânicos", "kg", 3.28, 720, 200, 500, 85.00, 140.00),
        ("Monoetanolamina", "Solventes e Outros", "kg", 1.01, 365, 1000, 3000, 14.50, 24.00),
        ("Nitrito de Sódio", "Sais e Inorgânicos", "kg", 2.17, 365, 1000, 3000, 6.20, 11.00),
        ("Nonilfenol Etoxilado 9.5", "Detergentes e Sanitizantes", "kg", 1.06, 365, 1500, 4000, 13.50, 22.00),
        ("Octaborato de Sódio", "Sais e Inorgânicos", "kg", 1.50, 720, 300, 800, 22.00, 38.00),
        ("Óxido de Magnésio", "Sais e Inorgânicos", "kg", 3.58, 720, 1000, 3000, 4.50, 8.50),
        ("Oxteril Bath", "Linha GR Especialidades", "L", 1.10, 180, 500, 1200, 16.00, 29.00),
        ("Oxteril Spray", "Linha GR Especialidades", "L", 1.05, 180, 500, 1200, 14.00, 25.00),
        ("Paraformaldeído", "Solventes e Outros", "kg", 1.46, 365, 500, 1500, 9.80, 17.00),
        ("Permanganato de Potássio – Em pó", "Peróxidos e Oxidantes", "kg", 2.70, 720, 500, 1500, 21.00, 36.00),
        ("Permanganato de Potássio – Solução", "Peróxidos e Oxidantes", "L", 1.08, 180, 500, 1500, 8.50, 15.00),
        ("Peróxido de Hidrogênio 35% (130V)", "Peróxidos e Oxidantes", "L", 1.13, 180, 2000, 6000, 3.80, 7.20),
        ("Peróxido de Hidrogênio 50% (200V)", "Peróxidos e Oxidantes", "L", 1.20, 180, 3000, 8000, 4.90, 9.10),
        ("Peróxido de Hidrogênio 60% (200V)", "Peróxidos e Oxidantes", "L", 1.24, 180, 2000, 5000, 6.10, 11.20),
        ("Policloreto de Alumínio 12%", "Tratamento de Água / Polímeros", "L", 1.20, 180, 3000, 10000, 2.50, 4.80),
        ("Policloreto de Alumínio 18%", "Tratamento de Água / Polímeros", "L", 1.35, 180, 4000, 12000, 3.40, 6.50),
        ("Policloreto de Alumínio 30% – Em pó", "Tratamento de Água / Polímeros", "kg", 0.85, 365, 2000, 6000, 7.20, 13.00),
        ("Propilenoglicol", "Solventes e Outros", "kg", 1.04, 365, 1000, 3000, 13.00, 22.00),
        ("Silicato de Sódio – Em pó", "Sais e Inorgânicos", "kg", 2.10, 720, 1000, 3000, 4.20, 8.00),
        ("Soda Cáustica – Escamas", "Bases e Álcalis", "kg", 2.13, 365, 3000, 10000, 6.50, 11.50),
        ("Soda Cáustica – Micropérolas", "Bases e Álcalis", "kg", 2.13, 365, 2000, 8000, 7.20, 12.80),
        ("Sorbitol 70%", "Solventes e Outros", "kg", 1.29, 365, 1000, 3000, 8.50, 15.00),
        ("Sulfato de Alumínio Ferroso – Granulado", "Tratamento de Água / Polímeros", "kg", 1.61, 720, 3000, 8000, 1.80, 3.50),
        ("Sulfato de Alumínio Ferroso – Líquido", "Tratamento de Água / Polímeros", "L", 1.32, 180, 4000, 12000, 1.20, 2.40),
        ("Sulfato de Alumínio Isento de Ferro – Granulado", "Tratamento de Água / Polímeros", "kg", 1.61, 720, 3000, 8000, 2.20, 4.20),
        ("Sulfato de Alumínio Isento de Ferro – Líquido", "Tratamento de Água / Polímeros", "L", 1.32, 180, 4000, 12000, 1.50, 3.00),
        ("Sulfato de Alumínio Isento de Ferro – Refinado", "Tratamento de Água / Polímeros", "kg", 1.61, 720, 2000, 5000, 2.80, 5.20),
        ("Sulfato de Amônio", "Sais e Inorgânicos", "kg", 1.77, 720, 2000, 6000, 2.10, 4.00),
        ("Sulfato de Cobalto", "Sais e Inorgânicos", "kg", 2.69, 720, 200, 500, 95.00, 160.00),
        ("Sulfato de Cobre 20% – Solução", "Sais e Inorgânicos", "L", 1.22, 365, 1000, 3000, 4.50, 8.80),
        ("Sulfato de Cobre 8% – Líquido", "Sais e Inorgânicos", "L", 1.08, 365, 1000, 3000, 2.20, 4.50),
        ("Sulfato de Cobre Pentahidratado", "Sais e Inorgânicos", "kg", 2.28, 720, 1000, 3000, 16.50, 28.00),
        ("Sulfato de Ferro", "Sais e Inorgânicos", "kg", 2.84, 365, 1000, 4000, 2.80, 5.20),
        ("Sulfato de Magnésio – Sólido", "Sais e Inorgânicos", "kg", 2.66, 720, 1000, 3000, 3.10, 6.00),
        ("Sulfato de Magnésio – Solução", "Sais e Inorgânicos", "L", 1.25, 365, 1000, 3000, 1.90, 3.80),
        ("Sulfato de Manganês", "Sais e Inorgânicos", "kg", 3.21, 720, 500, 1500, 8.50, 15.20),
        ("Sulfato de Sódio Anidro", "Sais e Inorgânicos", "kg", 2.66, 720, 2000, 6000, 1.90, 3.80),
        ("Sulfato de Zinco Heptahidratado", "Sais e Inorgânicos", "kg", 1.97, 720, 1000, 3000, 7.20, 13.00),
        ("Sulfato de Zinco Monohidratado", "Sais e Inorgânicos", "kg", 3.28, 720, 1000, 3000, 9.80, 17.50),
        ("Sulfato Férrico", "Tratamento de Água / Polímeros", "L", 1.50, 365, 2000, 6000, 4.10, 7.90),
        ("Sulfito de Sódio", "Sais e Inorgânicos", "kg", 2.63, 365, 1000, 3000, 4.50, 8.50),
        ("Tripolifosfato de Sódio", "Sais e Inorgânicos", "kg", 2.52, 720, 2000, 5000, 8.90, 15.50)
    ]

    for idx, (nome, cat_nome, um, dens, val, est_min, est_at, cust, prec) in enumerate(produtos_gr, start=101):
        codigo = f"GR-{idx}"
        cursor.execute("SELECT id FROM categorias WHERE nome = ?", (cat_nome,))
        cat_id = cursor.fetchone()[0]

        cursor.execute("""
        INSERT OR IGNORE INTO produtos 
        (codigo, nome, categoria_id, tipo, unidade_medida, densidade_g_ml, validade_dias, estoque_minimo, estoque_atual, custo_unitario, preco_venda_unitario)
        VALUES (?, ?, ?, 'Acabado', ?, ?, ?, ?, ?, ?, ?)
        """, (codigo, nome, cat_id, um, dens, val, est_min, est_at, cust, prec))

    conn.commit()
    conn.close()
    print("✅ Banco de Dados 'gr_cruzeiro_pcp.db' criado e populado com sucesso!")

if __name__ == "__main__":
    inicializar_banco_dados()