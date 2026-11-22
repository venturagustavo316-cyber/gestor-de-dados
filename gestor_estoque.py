"""Inicializa o sistema de gestão de estoque."""

from app.database import initialize_database
from app.ui import GestorEstoqueApp


if __name__ == "__main__":
    initialize_database()
    GestorEstoqueApp().mainloop()
