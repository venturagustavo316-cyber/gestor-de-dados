"""Interface gráfica do gestor de estoque."""

import sys
from pathlib import Path
from tkinter import messagebox, ttk

try:
    import customtkinter as ctk
except ModuleNotFoundError as error:
    if error.name != "customtkinter":
        raise
    raise SystemExit(
        "Dependência ausente: customtkinter. Instale com "
        "'py -m pip install -r requirements.txt' na pasta 'gestor de dados'."
    ) from error

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from app import repositories, services
else:
    from . import repositories, services


PRIMARY = "#2563eb"
PRIMARY_HOVER = "#1d4ed8"
SUCCESS = "#059669"
BACKGROUND = "#f4f7fb"
SURFACE = "#ffffff"
TEXT = "#172033"
MUTED = "#64748b"


def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_decimal(value):
    value = value.strip().replace("R$", "").replace(" ", "")
    if "," in value:
        value = value.replace(".", "").replace(",", ".")
    return float(value)


class GestorEstoqueApp(ctk.CTk):
    PAGES = {
        "Visão geral": ("Acompanhe os indicadores e a atividade recente do estoque.", "build_dashboard"),
        "Produtos": ("Consulte o catálogo e acompanhe os níveis de estoque.", "build_products"),
        "Movimentações": ("Veja as entradas registradas no almoxarifado.", "build_movements"),
    }

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.title("Gestor de Estoque")
        self.geometry("1280x780")
        self.minsize(1000, 650)
        self.configure(fg_color=BACKGROUND)
        self._configure_table_style()
        self._build_layout()
        self.show_page("Visão geral")

    def _configure_table_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Gestor.Treeview", rowheight=38, font=("Segoe UI", 10),
            background=SURFACE, fieldbackground=SURFACE, foreground=TEXT,
            borderwidth=0,
        )
        style.configure(
            "Gestor.Treeview.Heading", font=("Segoe UI", 10, "bold"),
            background="#eef2f7", foreground=MUTED, relief="flat", padding=10,
        )
        style.map("Gestor.Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", TEXT)])

    def _build_layout(self):
        sidebar = ctk.CTkFrame(self, width=242, corner_radius=0, fg_color="#111827")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ctk.CTkLabel(sidebar, text="◆  ESTOQUE", font=("Segoe UI", 22, "bold"), text_color="white").pack(anchor="w", padx=25, pady=(32, 3))
        ctk.CTkLabel(sidebar, text="ALMOXARIFADO CENTRAL", font=("Segoe UI", 10, "bold"), text_color="#94a3b8").pack(anchor="w", padx=27, pady=(0, 36))
        for label in self.PAGES:
            ctk.CTkButton(
                sidebar, text=f"  {label}", anchor="w", height=45, corner_radius=8,
                fg_color="transparent", hover_color="#263449", text_color="#e2e8f0",
                font=("Segoe UI", 13), command=lambda page=label: self.show_page(page),
            ).pack(fill="x", padx=14, pady=4)
        ctk.CTkButton(
            sidebar, text="＋  Registrar entrada", anchor="w", height=46,
            corner_radius=8, fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
            font=("Segoe UI", 13, "bold"), command=self.open_invoice,
        ).pack(fill="x", padx=14, pady=(28, 0))
        ctk.CTkLabel(sidebar, text="Banco de dados local · SQLite", text_color="#94a3b8", font=("Segoe UI", 10)).pack(side="bottom", anchor="w", padx=22, pady=22)

        main = ctk.CTkFrame(self, corner_radius=0, fg_color=BACKGROUND)
        main.pack(side="left", expand=True, fill="both")
        header = ctk.CTkFrame(main, fg_color=BACKGROUND)
        header.pack(fill="x", padx=38, pady=(30, 20))
        self.title_label = ctk.CTkLabel(header, text="", font=("Segoe UI", 27, "bold"), text_color=TEXT)
        self.title_label.pack(anchor="w")
        self.subtitle = ctk.CTkLabel(header, text="", font=("Segoe UI", 12), text_color=MUTED)
        self.subtitle.pack(anchor="w", pady=(4, 0))
        self.content = ctk.CTkFrame(main, fg_color="transparent")
        self.content.pack(expand=True, fill="both", padx=38, pady=(0, 32))

    def show_page(self, page):
        for child in self.content.winfo_children():
            child.destroy()
        description, builder = self.PAGES[page]
        self.title_label.configure(text=page)
        self.subtitle.configure(text=description)
        getattr(self, builder)()

    def stat_card(self, parent, label, value, accent, hint):
        card = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=12, border_width=1, border_color="#e8edf4")
        ctk.CTkLabel(card, text=label.upper(), text_color=MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20, pady=(18, 5))
        ctk.CTkLabel(card, text=value, text_color=accent, font=("Segoe UI", 27, "bold")).pack(anchor="w", padx=20)
        ctk.CTkLabel(card, text=hint, text_color=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=(2, 18))
        return card

    def build_dashboard(self):
        total, low, value, movements = repositories.dashboard_data()
        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.pack(fill="x", pady=(0, 22))
        stats = (
            ("Produtos cadastrados", str(total), PRIMARY, "Itens no catálogo"),
            ("Estoque baixo", str(low), "#dc2626" if low else SUCCESS, "No limite ou abaixo do mínimo"),
            ("Valor em estoque", format_currency(value), SUCCESS, "Custo estimado do saldo atual"),
        )
        for index, item in enumerate(stats):
            self.stat_card(cards, *item).grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 10, 0))
            cards.grid_columnconfigure(index, weight=1, uniform="stats")
        self.build_table(self.content, "Atividade recente", ("Data", "Produto", "Tipo", "Quantidade", "Referência"), movements)

    def build_table(self, parent, title, columns, rows):
        card = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=12, border_width=1, border_color="#e8edf4")
        card.pack(expand=True, fill="both")
        ctk.CTkLabel(card, text=title, text_color=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=20, pady=(18, 12))
        tree = ttk.Treeview(card, columns=columns, show="headings", style="Gestor.Treeview")
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=150, anchor="w")
        for row in rows:
            tree.insert("", "end", values=tuple(row))
        if not rows:
            ctk.CTkLabel(card, text="Nenhum registro encontrado.", text_color=MUTED).pack(pady=24)
        tree.pack(expand=True, fill="both", padx=14, pady=(0, 14))
        return tree

    def build_products(self):
        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 14))
        search = ctk.CTkEntry(toolbar, placeholder_text="Buscar por código ou nome", width=330, height=40)
        search.pack(side="left")
        search.bind("<Return>", lambda _event: self.render_product_table(search.get()))
        ctk.CTkButton(toolbar, text="Buscar", width=92, height=40, fg_color=PRIMARY, hover_color=PRIMARY_HOVER, command=lambda: self.render_product_table(search.get())).pack(side="left", padx=8)
        ctk.CTkButton(toolbar, text="＋  Novo produto", height=40, fg_color=SUCCESS, hover_color="#047857", command=self.open_product).pack(side="right")
        self.products_area = ctk.CTkFrame(self.content, fg_color="transparent")
        self.products_area.pack(expand=True, fill="both")
        self.render_product_table()

    def render_product_table(self, search=""):
        for child in self.products_area.winfo_children():
            child.destroy()
        products = repositories.list_products(search)
        rows = [
            (item["codigo"], item["nome"], item["unidade"], item["estoque_atual"], item["estoque_minimo"], format_currency(item["preco"]))
            for item in products
        ]
        tree = self.build_table(self.products_area, f"Produtos · {len(rows)} encontrados", ("Código", "Produto", "Un.", "Estoque", "Mínimo", "Preço"), rows)
        for item, product in zip(tree.get_children(), products):
            if product["estoque_atual"] <= product["estoque_minimo"]:
                tree.item(item, tags=("low_stock",))
        tree.tag_configure("low_stock", foreground="#b91c1c")

    def build_movements(self):
        self.build_table(self.content, "Movimentações recentes", ("Data", "Produto", "Tipo", "Quantidade", "Referência"), repositories.list_movements())

    def open_product(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Novo produto")
        modal.geometry("440x520")
        modal.resizable(False, False)
        modal.transient(self)
        modal.grab_set()
        modal.configure(fg_color=BACKGROUND)
        ctk.CTkLabel(modal, text="Cadastrar produto", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(pady=(28, 5))
        ctk.CTkLabel(modal, text="Preencha os dados para incluir no catálogo.", text_color=MUTED).pack(pady=(0, 20))
        form = ctk.CTkFrame(modal, fg_color=SURFACE, corner_radius=12)
        form.pack(fill="x", padx=28)
        fields = {}
        for key, label in (("codigo", "Código"), ("nome", "Nome do produto"), ("unidade", "Unidade"), ("preco", "Preço unitário (R$)"), ("minimo", "Estoque mínimo")):
            ctk.CTkLabel(form, text=label, text_color=TEXT).pack(anchor="w", padx=18, pady=(12, 4))
            fields[key] = ctk.CTkEntry(form, height=36)
            fields[key].pack(fill="x", padx=18)
        fields["unidade"].insert(0, "UN")

        def save():
            try:
                codigo, nome = fields["codigo"].get().strip(), fields["nome"].get().strip()
                unidade = fields["unidade"].get().strip() or "UN"
                preco, minimo = parse_decimal(fields["preco"].get()), int(fields["minimo"].get())
                if not codigo or not nome or preco < 0 or minimo < 0:
                    raise ValueError("Informe código, nome e valores iguais ou maiores que zero.")
                repositories.add_product(codigo, nome, unidade, preco, minimo)
                modal.destroy()
                self.show_page("Produtos")
            except ValueError as error:
                messagebox.showwarning("Revise os dados", str(error), parent=modal)
            except Exception as error:
                messagebox.showerror("Não foi possível salvar", str(error), parent=modal)

        ctk.CTkButton(modal, text="Salvar produto", height=42, fg_color=PRIMARY, hover_color=PRIMARY_HOVER, command=save).pack(fill="x", padx=28, pady=20)

    def open_invoice(self):
        InvoiceWindow(self, on_saved=lambda: self.show_page("Visão geral"))


class InvoiceWindow(ctk.CTkToplevel):
    def __init__(self, master, on_saved):
        super().__init__(master)
        self.on_saved = on_saved
        self.items = []
        self.title("Entrada de nota fiscal")
        self.geometry("1000x680")
        self.minsize(850, 600)
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=BACKGROUND)
        ctk.CTkLabel(self, text="Nova entrada de nota fiscal", font=("Segoe UI", 23, "bold"), text_color=TEXT).pack(anchor="w", padx=30, pady=(25, 16))
        form = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=12)
        form.pack(fill="x", padx=30)
        self.number = self._field(form, "Número da nota", 0)
        self.serie = self._field(form, "Série", 1)
        suppliers = repositories.list_suppliers()
        self.supplier_by_name = {supplier["nome"]: supplier["id"] for supplier in suppliers}
        ctk.CTkLabel(form, text="Fornecedor", text_color=TEXT).grid(row=0, column=4, padx=(12, 6), pady=18, sticky="w")
        self.supplier = ctk.CTkComboBox(form, values=list(self.supplier_by_name) or ["Nenhum fornecedor cadastrado"], width=280, height=36)
        self.supplier.grid(row=0, column=5, padx=(0, 18), pady=18)
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=30, pady=(22, 10))
        ctk.CTkLabel(toolbar, text="Itens da nota", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkButton(toolbar, text="＋  Adicionar item", fg_color=PRIMARY, hover_color=PRIMARY_HOVER, command=self.add_item).pack(side="right")
        self.items_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.items_frame.pack(expand=True, fill="both", padx=30)
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=30, pady=16)
        self.total_label = ctk.CTkLabel(bottom, text="Total: R$ 0,00", font=("Segoe UI", 19, "bold"), text_color=TEXT)
        self.total_label.pack(side="left")
        ctk.CTkButton(bottom, text="Gravar entrada", fg_color=SUCCESS, hover_color="#047857", height=42, command=self.save).pack(side="right")
        self.render_items()

    @staticmethod
    def _field(parent, label, column):
        ctk.CTkLabel(parent, text=label, text_color=TEXT).grid(row=0, column=column * 2, padx=(18 if column == 0 else 10, 6), pady=18, sticky="w")
        entry = ctk.CTkEntry(parent, width=130, height=36)
        entry.grid(row=0, column=column * 2 + 1, padx=(0, 8), pady=18)
        return entry

    def add_item(self):
        products = repositories.list_products()
        if not products:
            messagebox.showinfo("Catálogo vazio", "Cadastre um produto antes de lançar a entrada.", parent=self)
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Adicionar item")
        dialog.geometry("440x370")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        by_name = {f"{product['codigo']} — {product['nome']}": product for product in products}
        ctk.CTkLabel(dialog, text="Produto", text_color=TEXT).pack(anchor="w", padx=30, pady=(26, 5))
        choice = ctk.CTkComboBox(dialog, values=list(by_name), width=370, height=36)
        choice.pack(padx=30)
        ctk.CTkLabel(dialog, text="Quantidade", text_color=TEXT).pack(anchor="w", padx=30, pady=(16, 5))
        qty = ctk.CTkEntry(dialog, height=36)
        qty.pack(fill="x", padx=30)
        ctk.CTkLabel(dialog, text="Preço unitário (R$)", text_color=TEXT).pack(anchor="w", padx=30, pady=(16, 5))
        price = ctk.CTkEntry(dialog, height=36)
        price.pack(fill="x", padx=30)

        def include():
            try:
                product = by_name[choice.get()]
                quantity, unit_price = int(qty.get()), parse_decimal(price.get())
                if quantity <= 0 or unit_price < 0:
                    raise ValueError
                self.items.append({"produto_id": product["id"], "produto": product["nome"], "quantidade": quantity, "preco": unit_price})
                dialog.destroy()
                self.render_items()
            except (ValueError, KeyError):
                messagebox.showwarning("Dados inválidos", "Informe uma quantidade positiva e um preço válido.", parent=dialog)

        ctk.CTkButton(dialog, text="Incluir item", height=40, fg_color=PRIMARY, hover_color=PRIMARY_HOVER, command=include).pack(fill="x", padx=30, pady=22)

    def render_items(self):
        for child in self.items_frame.winfo_children():
            child.destroy()
        rows = [(item["produto"], item["quantidade"], format_currency(item["preco"]), format_currency(item["quantidade"] * item["preco"])) for item in self.items]
        self.tree = self._build_items_table(rows)
        self.total_label.configure(text=f"Total: {format_currency(sum(item['quantidade'] * item['preco'] for item in self.items))}")

    def _build_items_table(self, rows):
        card = ctk.CTkFrame(self.items_frame, fg_color=SURFACE, corner_radius=12, border_width=1, border_color="#e8edf4")
        card.pack(expand=True, fill="both")
        columns = ("Produto", "Quantidade", "Preço unitário", "Total")
        tree = ttk.Treeview(card, columns=columns, show="headings", style="Gestor.Treeview")
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=190, anchor="w")
        for row in rows:
            tree.insert("", "end", values=row)
        if not rows:
            ctk.CTkLabel(card, text="Adicione os produtos que constam na nota.", text_color=MUTED).pack(pady=25)
        tree.pack(expand=True, fill="both", padx=14, pady=14)
        return tree

    def save(self):
        try:
            total = services.register_incoming_invoice(
                self.number.get(), self.serie.get(),
                self.supplier_by_name.get(self.supplier.get()), self.items,
            )
            messagebox.showinfo("Entrada registrada", f"Nota gravada com sucesso. Total: {format_currency(total)}", parent=self)
            self.on_saved()
            self.destroy()
        except ValueError as error:
            messagebox.showwarning("Revise a nota", str(error), parent=self)
        except Exception as error:
            messagebox.showerror("Erro ao salvar", str(error), parent=self)


if __name__ == "__main__":
    from app.database import initialize_database

    initialize_database()
    GestorEstoqueApp().mainloop()
