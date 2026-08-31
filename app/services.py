from datetime import date

from .database import connect


def register_incoming_invoice(numero, serie, fornecedor_id, items):
    """Grava a nota, seus itens e o aumento de saldo em uma única transação."""
    if not numero.strip() or not items:
        raise ValueError("Informe o número da nota e pelo menos um item.")
    if not fornecedor_id:
        raise ValueError("Selecione um fornecedor.")

    total = sum(item["quantidade"] * item["preco"] for item in items)
    with connect() as connection:
        cursor = connection.execute(
            """INSERT INTO notas_fiscais
               (numero, serie, fornecedor_id, emissao, total)
               VALUES (?, ?, ?, ?, ?)""",
            (numero, serie, fornecedor_id, date.today().isoformat(), total),
        )
        nota_id = cursor.lastrowid
        for item in items:
            connection.execute(
                """INSERT INTO itens_nota_fiscal
                   (nota_fiscal_id, produto_id, quantidade, preco_unitario)
                   VALUES (?, ?, ?, ?)""",
                (nota_id, item["produto_id"], item["quantidade"], item["preco"]),
            )
            connection.execute(
                "UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
            connection.execute(
                """INSERT INTO movimentacoes_estoque
                   (produto_id, tipo, quantidade, data, referencia)
                   VALUES (?, 'Entrada NF', ?, ?, ?)""",
                (item["produto_id"], item["quantidade"], date.today().isoformat(), f"NF {numero}"),
            )
    return total
