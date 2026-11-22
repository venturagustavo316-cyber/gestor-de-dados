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
    codigo, nome, unidade = codigo.strip(), nome.strip(), unidade.strip() or "UN"
    if not codigo or not nome:
        raise ValueError("Informe o código e o nome do produto.")
    if preco < 0 or minimo < 0:
        raise ValueError("Preço e estoque mínimo devem ser iguais ou maiores que zero.")
    with connect() as connection:
        connection.execute(
            """INSERT INTO produtos (codigo, nome, unidade, preco, estoque_minimo)
               VALUES (?, ?, ?, ?, ?)""",
            (codigo, nome, unidade, preco, minimo),
        )


def _recent_movements(connection, limit=12):
    return connection.execute(
        """SELECT m.data, p.nome, m.tipo, m.quantidade, m.referencia
           FROM movimentacoes_estoque AS m
           JOIN produtos AS p ON p.id = m.produto_id
           ORDER BY m.id DESC LIMIT ?""",
        (limit,),
    ).fetchall()


def list_movements(limit=12):
    with connect() as connection:
        return _recent_movements(connection, limit)


def dashboard_data():
    with connect() as connection:
        total = connection.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
        low = connection.execute(
            "SELECT COUNT(*) FROM produtos WHERE estoque_atual <= estoque_minimo"
        ).fetchone()[0]
        value = connection.execute(
            "SELECT COALESCE(SUM(preco * estoque_atual), 0) FROM produtos"
        ).fetchone()[0]
        movements = _recent_movements(connection)
        return total, low, value, movements
