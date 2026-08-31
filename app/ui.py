import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

from . import repositories, services


PRIMARY = "#1d4ed8"
SURFACE = "#ffffff"
BACKGROUND = "#f1f5f9"
TEXT = "#0f172a"


class GestorEstoqueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Dados | Almoxarifado")
        self.geometry("1250x760")
        self.minsize(1050, 650)
        ctk.set_appearance_mode("light")
        self.configure(fg_color=BACKGROUND)
        self._configure_table_style()
        self._build_layout()
        self.show_page("Visão geral")

    def _configure_table_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Gestor.Treeview", rowheight=31, font=("Segoe UI", 10), background="white", fieldbackground="white", foreground=TEXT)
        style.configure("Gestor.Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0", foreground=TEXT, relief="flat")
        style.map("Gestor.Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", TEXT)])

    def _build_layout(self):
        sidebar = ctk.CTkFrame(self, width=225, corner_radius=0, fg_color="#0f172a")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ctk.CTkLabel(sidebar, text="GESTOR", font=("Segoe UI", 25, "bold"), text_color="white").pack(anchor="w", padx=24, pady=(32, 0))
        ctk.CTkLabel(sidebar, text="ALMOXARIFADO CENTRAL", font=("Segoe UI", 10, "bold"), text_color="#94a3b8").pack(anchor="w", padx=25, pady=(0, 30))
        for label in ("Visão geral", "Produtos", "Movimentações"):
            ctk.CTkButton(sidebar, text=label, anchor="w", height=42, corner_radius=7, fg_color="transparent", hover_color="#1e293b", font=("Segoe UI", 13), command=lambda p=label: self.show_page(p)).pack(fill="x", padx=14, pady=3)
        ctk.CTkButton(sidebar, text="+  Nova entrada (NF)", anchor="w", height=43, corner_radius=7, fg_color=PRIMARY, hover_color="#1e40af", font=("Segoe UI", 13, "bold"), command=self.open_invoice).pack(fill="x", padx=14, pady=(24, 0))
        ctk.CTkLabel(sidebar, text="SQLite local • Demonstração", text_color="#64748b", font=("Segoe UI", 10)).pack(side="bottom", anchor="w", padx=22, pady=22)

        main = ctk.CTkFrame(self, corner_radius=0, fg_color=BACKGROUND)
        main.pack(side="left", expand=True, fill="both")
        self.title_label = ctk.CTkLabel(main, text="", font=("Segoe UI", 25, "bold"), text_color=TEXT)
        self.title_label.pack(anchor="w", padx=34, pady=(30, 4))
        self.subtitle = ctk.CTkLabel(main, text="", font=("Segoe UI", 12), text_color="#64748b")
        self.subtitle.pack(anchor="w", padx=34, pady=(0, 18))
        self.content = ctk.CTkFrame(main, fg_color="transparent")
        self.content.pack(expand=True, fill="both", padx=34, pady=(0, 30))

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def show_page(self, page):
        self.clear_content()
        self.title_label.configure(text=page)
        descriptions = {"Visão geral": "Acompanhe o saldo e as movimentações do almoxarifado.", "Produtos": "Catálogo e níveis de estoque disponíveis.", "Movimentações": "Últimas entradas registradas no sistema."}
        self.subtitle.configure(text=descriptions[page])
        {"Visão geral": self.build_dashboard, "Produtos": self.build_products, "Movimentações": self.build_movements}[page]()

    def stat_card(self, parent, label, value, accent):
        card = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=10)
        ctk.CTkLabel(card, text=label.upper(), text_color="#64748b", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(card, text=value, text_color=accent, font=("Segoe UI", 25, "bold")).pack(anchor="w", padx=18, pady=(0, 16))
        return card

    def build_dashboard(self):
        total, low, value, movements = repositories.dashboard_data()
        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.pack(fill="x", pady=(0, 20))
        for text, number, color in (("Produtos cadastrados", str(total), PRIMARY), ("Abaixo do mínimo", str(low), "#dc2626"), ("Valor em estoque", f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), "#059669")):
            self.stat_card(cards, text, number, color).pack(side="left", expand=True, fill="x", padx=(0, 12))
        self.build_table("Últimas movimentações", ("Data", "Produto", "Tipo", "Quantidade", "Referência"), movements)

    def build_table(self, title, columns, rows):
        card = ctk.CTkFrame(self.content, fg_color=SURFACE, corner_radius=10)
        card.pack(expand=True, fill="both")
        ctk.CTkLabel(card, text=title, text_color=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=20, pady=(18, 10))
        tree = ttk.Treeview(card, columns=columns, show="headings", style="Gestor.Treeview")
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=130, anchor="w")
        for row in rows:
            tree.insert("", "end", values=tuple(row))
        tree.pack(expand=True, fill="both", padx=16, pady=(0, 16))
        return tree

    def build_products(self):
        toolbar = ctk.CTkFrame(self.content, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))
        search = ctk.CTkEntry(toolbar, placeholder_text="Buscar por código ou produto", width=270, height=35)
        search.pack(side="left")
        ctk.CTkButton(toolbar, text="Buscar", width=80, height=35, fg_color=PRIMARY, command=lambda: self.render_product_table(search.get())).pack(side="left", padx=7)
        ctk.CTkButton(toolbar, text="+ Novo produto", width=120, height=35, fg_color="#059669", command=self.open_product).pack(side="right")
        self.products_area = ctk.CTkFrame(self.content, fg_color="transparent")
        self.products_area.pack(expand=True, fill="both")
        self.render_product_table()

    def render_product_table(self, search=""):
        for child in self.products_area.winfo_children(): child.destroy()
        rows = repositories.list_products(search)
        formatted = [(r["codigo"], r["nome"], r["unidade"], r["estoque_atual"], r["estoque_minimo"], f"R$ {r['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")) for r in rows]
        self.build_table_in(self.products_area, "Produtos", ("Código", "Produto", "Un.", "Estoque", "Mínimo", "Preço"), formatted)

    def build_table_in(self, parent, title, columns, rows):
        card = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=10); card.pack(expand=True, fill="both")
        ctk.CTkLabel(card, text=title, text_color=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=20, pady=(18, 10))
        tree = ttk.Treeview(card, columns=columns, show="headings", style="Gestor.Treeview")
        for col in columns: tree.heading(col, text=col); tree.column(col, width=120)
        for row in rows: tree.insert("", "end", values=row)
        tree.pack(expand=True, fill="both", padx=16, pady=(0, 16))

    def build_movements(self):
        self.build_table("Movimentações recentes", ("Data", "Produto", "Tipo", "Quantidade", "Referência"), repositories.dashboard_data()[3])

    def open_product(self):
        modal = ctk.CTkToplevel(self); modal.title("Novo produto"); modal.geometry("430x440"); modal.transient(self); modal.grab_set()
        ctk.CTkLabel(modal, text="Cadastrar produto", font=("Segoe UI", 20, "bold")).pack(pady=(25, 18))
        fields = {}
        for key, label in (("codigo", "Código"), ("nome", "Nome"), ("unidade", "Unidade"), ("preco", "Preço"), ("minimo", "Estoque mínimo")):
            ctk.CTkLabel(modal, text=label).pack(anchor="w", padx=38)
            fields[key] = ctk.CTkEntry(modal, height=32); fields[key].pack(fill="x", padx=38, pady=(0, 8))
        fields["unidade"].insert(0, "UN")
        def save():
            try:
                repositories.add_product(fields["codigo"].get(), fields["nome"].get(), fields["unidade"].get(), float(fields["preco"].get().replace(",", ".")), int(fields["minimo"].get()))
                modal.destroy(); self.show_page("Produtos")
            except Exception as error: messagebox.showerror("Não foi possível salvar", str(error), parent=modal)
        ctk.CTkButton(modal, text="Salvar produto", fg_color=PRIMARY, command=save).pack(fill="x", padx=38, pady=16)

    def open_invoice(self):
        InvoiceWindow(self, on_saved=lambda: self.show_page("Visão geral"))


class InvoiceWindow(ctk.CTkToplevel):
    def __init__(self, master, on_saved):
        super().__init__(master); self.on_saved = on_saved; self.items = []
        self.title("Entrada de nota fiscal"); self.geometry("980x650"); self.transient(master); self.grab_set(); self.configure(fg_color=BACKGROUND)
        ctk.CTkLabel(self, text="Nova entrada de nota fiscal", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(anchor="w", padx=28, pady=(24, 14))
        form = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=10); form.pack(fill="x", padx=28)
        self.number = self._field(form, "Número", 0); self.serie = self._field(form, "Série", 1)
        suppliers = repositories.list_suppliers(); self.supplier_by_name = {s["nome"]: s["id"] for s in suppliers}
        ctk.CTkLabel(form, text="Fornecedor", text_color=TEXT).grid(row=0, column=4, padx=(15, 6), pady=16, sticky="w")
        self.supplier = ctk.CTkComboBox(form, values=list(self.supplier_by_name) or ["Cadastre um fornecedor"], width=300); self.supplier.grid(row=0, column=5, padx=(0, 18), pady=16)
        item_bar = ctk.CTkFrame(self, fg_color="transparent"); item_bar.pack(fill="x", padx=28, pady=(22, 8))
        ctk.CTkLabel(item_bar, text="Itens da nota", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkButton(item_bar, text="+ Adicionar item", fg_color=PRIMARY, command=self.add_item).pack(side="right")
        self.tree_frame = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=10); self.tree_frame.pack(expand=True, fill="both", padx=28)
        self.total_label = ctk.CTkLabel(self, text="Total: R$ 0,00", font=("Segoe UI", 18, "bold"), text_color=TEXT); self.total_label.pack(anchor="e", padx=32, pady=12)
        ctk.CTkButton(self, text="Gravar entrada e atualizar estoque", fg_color="#059669", height=40, command=self.save).pack(anchor="e", padx=28, pady=(0, 24))
        self.render_items()

    def _field(self, parent, label, col):
        ctk.CTkLabel(parent, text=label, text_color=TEXT).grid(row=0, column=col * 2, padx=(18 if col == 0 else 10, 6), pady=16, sticky="w")
        entry = ctk.CTkEntry(parent, width=130); entry.grid(row=0, column=col * 2 + 1, padx=(0, 8), pady=16)
        return entry

    def add_item(self):
        products = repositories.list_products()
        if not products: return
        dialog = ctk.CTkToplevel(self); dialog.title("Adicionar item"); dialog.geometry("420x350"); dialog.transient(self); dialog.grab_set()
        by_name = {f"{p['codigo']} — {p['nome']}": p for p in products}
        ctk.CTkLabel(dialog, text="Produto").pack(anchor="w", padx=30, pady=(26, 2)); choice = ctk.CTkComboBox(dialog, values=list(by_name), width=350); choice.pack(padx=30)
        ctk.CTkLabel(dialog, text="Quantidade").pack(anchor="w", padx=30, pady=(14, 2)); qty = ctk.CTkEntry(dialog, width=350); qty.pack(padx=30)
        ctk.CTkLabel(dialog, text="Preço unitário").pack(anchor="w", padx=30, pady=(14, 2)); price = ctk.CTkEntry(dialog, width=350); price.pack(padx=30)
        def include():
            try:
                product = by_name[choice.get()]; self.items.append({"produto_id": product["id"], "produto": product["nome"], "quantidade": int(qty.get()), "preco": float(price.get().replace(",", "."))}); dialog.destroy(); self.render_items()
            except (ValueError, KeyError): messagebox.showerror("Dados inválidos", "Escolha um produto e informe quantidade e preço válidos.", parent=dialog)
        ctk.CTkButton(dialog, text="Incluir item", fg_color=PRIMARY, command=include).pack(fill="x", padx=30, pady=22)

    def render_items(self):
        for child in self.tree_frame.winfo_children(): child.destroy()
        tree = ttk.Treeview(self.tree_frame, columns=("Produto", "Quantidade", "Preço unit.", "Total"), show="headings", style="Gestor.Treeview")
        for col in ("Produto", "Quantidade", "Preço unit.", "Total"): tree.heading(col, text=col); tree.column(col, width=180)
        for item in self.items: tree.insert("", "end", values=(item["produto"], item["quantidade"], f"R$ {item['preco']:.2f}", f"R$ {item['quantidade'] * item['preco']:.2f}"))
        tree.pack(expand=True, fill="both", padx=12, pady=12)
        total = sum(i["quantidade"] * i["preco"] for i in self.items); self.total_label.configure(text=f"Total: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def save(self):
        try:
            total = services.register_incoming_invoice(self.number.get(), self.serie.get(), self.supplier_by_name.get(self.supplier.get()), self.items)
            messagebox.showinfo("Entrada registrada", f"Nota gravada com sucesso. Total: R$ {total:,.2f}", parent=self); self.on_saved(); self.destroy()
        except ValueError as error: messagebox.showwarning("Revise a nota", str(error), parent=self)
        except Exception as error: messagebox.showerror("Erro ao salvar", str(error), parent=self)
