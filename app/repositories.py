from .database import connect


def list_products(search=""):
    with connect() as connection:
        return connection.execute(
            """SELECT * FROM produtos
               WHERE codigo LIKE ? OR nome LIKE ?
               ORDER BY nome""",
            (f"%{search}%", f"%{search}%"),
        ).fetchall()


def list_suppliers():
    with connect() as connection:
        return connection.execute("SELECT * FROM fornecedores ORDER BY nome").fetchall()


def add_product(codigo, nome, unidade, preco, minimo):
    with connect() as connection:
        connection.execute(
            """INSERT INTO produtos (codigo, nome, unidade, preco, estoque_minimo)
               VALUES (?, ?, ?, ?, ?)""",
            (codigo, nome, unidade, preco, minimo),
        )


def dashboard_data():
    with connect() as connection:
        total = connection.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
        low = connection.execute(
            "SELECT COUNT(*) FROM produtos WHERE estoque_atual <= estoque_minimo"
        ).fetchone()[0]
        value = connection.execute(
            "SELECT COALESCE(SUM(preco * estoque_atual), 0) FROM produtos"
        ).fetchone()[0]
        movements = connection.execute(
            """SELECT m.data, p.nome, m.tipo, m.quantidade, m.referencia
               FROM movimentacoes_estoque m JOIN produtos p ON p.id = m.produto_id
               ORDER BY m.id DESC LIMIT 12"""
        ).fetchall()
        return total, low, value, movements
