from pathlib import Path
import sqlite3


DATABASE_PATH = Path(__file__).resolve().parent.parent / "gestor_estoque.db"


def connect():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                unidade TEXT NOT NULL DEFAULT 'UN',
                preco REAL NOT NULL DEFAULT 0,
                estoque_atual INTEGER NOT NULL DEFAULT 0,
                estoque_minimo INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                documento TEXT
            );

            CREATE TABLE IF NOT EXISTS notas_fiscais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL,
                serie TEXT,
                fornecedor_id INTEGER NOT NULL,
                emissao TEXT NOT NULL,
                total REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Lançada',
                FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
            );

            CREATE TABLE IF NOT EXISTS itens_nota_fiscal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nota_fiscal_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                FOREIGN KEY (nota_fiscal_id) REFERENCES notas_fiscais(id),
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            );

            CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                data TEXT NOT NULL,
                referencia TEXT,
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            );
            """
        )
        exists = connection.execute("SELECT 1 FROM produtos LIMIT 1").fetchone()
        if not exists:
            connection.executemany(
                """INSERT INTO produtos
                   (codigo, nome, unidade, preco, estoque_atual, estoque_minimo)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [
                    ("001", "Notebook corporativo", "UN", 3000, 5, 2),
                    ("002", "Monitor 22 polegadas", "UN", 900, 9, 3),
                    ("003", "Teclado USB", "UN", 120, 18, 5),
                ],
            )
            connection.execute(
                "INSERT INTO fornecedores (nome, documento) VALUES (?, ?)",
                ("Fornecedor demonstração", "00.000.000/0001-00"),
            )
