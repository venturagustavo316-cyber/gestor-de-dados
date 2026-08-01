import sqlite3
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from pyzbar import pyzbar
import cv2 as cv
from PIL import Image
import os



janela = ctk.CTk()
janela.title("banco de dados")
janela.geometry('700x500')
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")



conexao = sqlite3.connect("registro_de_usuarios.db")
cursor = conexao.cursor()
tree_usuario = None
tree_produtos = None
overlays = {}
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))
PASTA_ICONES = os.path.join(DIRETORIO_BASE, "icons")

def carregar_icone(icones, tamanho=(20,20)):
    caminho = os.path.join(PASTA_ICONES, icones)
    return ctk.CTkImage(Image.open(caminho), size=tamanho)

icone_add = carregar_icone("user_add.png")
icone_delete_user = carregar_icone("delete_user.png")
icone_user_add = carregar_icone("user.png")
icone_list_user = carregar_icone("list_user.png")
icone_sair = carregar_icone("sair.png")



def mostrar_overlay(nome):
    for chave, frame in overlays.items():
        frame.place_forget()
    overlays[nome].place(relx=0, rely=0, relwidth=1, relheight=1)
    overlays[nome].lift()

def esconder_overlay(nome):
    overlays[nome].place_forget()
    




#leitor de codigo de barras

def add_de_produtos():
    janela_add_produtos = ctk.CTkToplevel(janela)
    janela_add_produtos.title("cadatre o produto desejado")
    janela_add_produtos.geometry("600x600")

    text = ctk.CTkLabel(janela_add_produtos, text="digite as credencias do produto")
    text.pack()

    ctk.CTkLabel(janela_add_produtos, text="Nome").pack()
    entry_novo_nome = ctk.CTkEntry(janela_add_produtos)
    entry_novo_nome.pack()

    ctk.CTkLabel(janela_add_produtos, text="Preco").pack()
    entry_novo_preco = ctk.CTkEntry(janela_add_produtos)
    entry_novo_preco.pack()

    ctk.CTkLabel(janela_add_produtos, text="Quantidade").pack()
    entry_quantidade = ctk.CTkEntry(janela_add_produtos)
    entry_quantidade.pack()


    label_status_add_produto = ctk.CTkLabel(janela_add_produtos, text="")
    label_status_add_produto.pack()

    def salvar_alteracoes_produto():
        
        nome_novo = entry_novo_nome.get()
        try:
            preco_novo = float(entry_novo_preco.get())
        except ValueError:
            label_status_add_produto.configure(text="digite uma preco invalida (apenas numeros)")
            return
        try:
            quantidade_nova = int(entry_quantidade.get())
        except ValueError:
            label_status_add_produto.configure(text="digite apenas numeros")
        try:
            cursor.execute(
                "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)", 
                (nome_novo, preco_novo, quantidade_nova))
            conexao.commit()
            label_status_add_produto.configure(text="produto cadastrado")
        except sqlite3.IntegrityError:
            label_status_add_produto.configure(text="produto nao cadastrado")

    ctk.CTkButton(janela_add_produtos, text="salvar produto", command=salvar_alteracoes_produto).pack(padx=10, pady=2)
    ctk.CTkButton(janela_add_produtos, text="SAIR", command=janela_add_produtos.destroy).pack(padx=10, pady=2)
    # ctk.CTkButton(janela_add_produtos, text="Ler Codigo De Barras", command=leitor_de_produtos).pack(padx=10, pady=2)

    
def remover_produto(id_produto):
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
    conexao.commit()
    
def cria_overlay_remover_produto():
    frame = ctk.CTkFrame(janela)
    overlays["remover produto"] = frame


    ctk.CTkLabel(frame, text="digite o id do produto que deseja remover").pack()
    
    
    entry_id = ctk.CTkEntry(frame)
    entry_id.pack() 

    label_status_remover = ctk.CTkLabel(frame, text="")
    label_status_remover.pack()


    def mostra_produto():
        global tree_produtos

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="#2a2d2e", foreground="white", borderwidth=0)
        style.configure("Treeview", background="#292929", foreground="white", fieldbackground="#292929", borderwidth=0)
        style.map("Treeview", background=[('selected', '#3a3a3a')])

        
        if tree_produtos is None:
            colunas = ("ID", "NOME", "PRECO", "QUANTIDADE")
            tree_produtos = ttk.Treeview(frame, columns=colunas, show="headings")
            for col in colunas:
                tree_produtos.heading(col, text=col)
            tree_produtos.pack(fill=tk.BOTH, expand=True)
            
        tree_produtos.delete(*tree_produtos.get_children())
        cursor.execute("SELECT * FROM produtos ORDER BY nome ASC")
        for linha in cursor.fetchall():
            tree_produtos.insert("", tk.END, values=linha)

        tree_produtos.pack(padx=20, pady=20, fill="both", expand=True)





    def confirmar_remocao():
        try:
            id_produto = int(entry_id.get())
        except ValueError:
            label_status_remover.config(text="digite apenas o id(numero)")
            return

        cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
        if cursor.fetchone() is None:
            label_status_remover.config(text="esse id nao existe")
            return        
        remover_produto(id_produto)
        label_status_remover.config(text="produto removido")
        conexao.commit()



    
    ctk.CTkButton(frame, text="remover produto", command=confirmar_remocao).pack(pady=2)
    ctk.CTkButton(frame, text="fechar", command=lambda: esconder_overlay("remover produto")).pack(pady=2)
    ctk.CTkButton(frame, text="mostrar produtos", command=lambda: mostra_produto()).pack(pady=2)



#--------------------------------------SEM FUNCIONALIDADE----------------------------------------------------------

# def leitor_de_produtos():
#     FONTE_VIDEO = ""
#     camera_leitor = ctk.CTkToplevel(add_de_produtos)
#     camera_leitor.title("barcode")
#     camera_leitor.geometry("500X500")

#     label_status_barcode = ctk.CTkLabel(camera_leitor, text="")
#     label_status_barcode.pack()

#     cap = cv.VideoCapture(FONTE_VIDEO)
#     codigo_lidos = set()
#     ret, frame = cap.read()

#     if not ret:
#         label_status_barcode.configure(text="nao foi possivel ler o codigo de barras")
#         return
#     codigos = pyzbar.decode(frame)

#     for codigo in codigos:
#         dados = codigo.data.decode("utf-8")
#         tipo = codigo.type

#         (x, y, w, h) = codigo.rect
#         cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         cv.putText(frame)

#-------------------------------------------------------------------------------------------------------------------



#==========================================================CADASTRO DE USUARIO=================================================================================================
def criar_overlay_atualizar_cadastro():
    frame = ctk.CTkFrame(janela)
    overlays["atualizar cadastro"] = frame


    text = ctk.CTkLabel(frame, text="digite o id do usuario que deseja alterar")
    text.pack()

    ctk.CTkLabel(frame, text="ID").pack()
    entry_id_atualizar = ctk.CTkEntry(frame)
    entry_id_atualizar.pack()
    


    ctk.CTkLabel(frame, text="Nome").pack()
    entry_novo_nome = ctk.CTkEntry(frame)
    entry_novo_nome.pack()

    ctk.CTkLabel(frame, text="Idade").pack()
    entry_nova_idade = ctk.CTkEntry(frame)
    entry_nova_idade.pack()

    ctk.CTkLabel(frame, text="Email").pack()
    entry_novo_email = ctk.CTkEntry(frame)
    entry_novo_email.pack()

    ctk.CTkLabel(frame, text="Telefone").pack()
    entry_novo_telefone = ctk.CTkEntry(frame)
    entry_novo_telefone.pack()


    label_status_atualizar = ctk.CTkLabel(frame, text="")
    label_status_atualizar.pack()

    id_confirmar = {"valor":None}

    def confirmar_id():
        try:
            id_atualizar = int(entry_id_atualizar.get())
        except ValueError:
            label_status_atualizar.config(text="digite apenas o id(numero)")
            return
        cursor.execute("SELECT nome, idade, email, telefone FROM registros WHERE id = ?", (id_atualizar,))
        resultado = cursor.fetchone()

        if resultado is None:
            label_status_atualizar.config(text="esse id nao existe")
            id_confirmar["valor"] = None
            return
        
        nome, idade, email, telefone = resultado

        
        
        entry_novo_nome.delete(0, tk.END)
        entry_novo_nome.insert(0, nome)

        entry_nova_idade.delete(0, tk.END)
        entry_nova_idade.insert(0, idade)

        entry_novo_email.delete(0, tk.END)
        entry_novo_email.insert(0, email)

        entry_novo_telefone.delete(0, tk.END)
        entry_novo_telefone.insert(0, telefone)

        id_confirmar["valor"] = id_atualizar
        label_status_atualizar.configure(text="usuario encontrado atualize os campos")

    def salvar_alteracoes():
        if id_confirmar["valor"] is None:
            label_status_atualizar.configure(text="confirme um id valido antes de salvar")
            return
        
        nome_novo = entry_novo_nome.get()
        try:
            idade_nova = int(entry_nova_idade.get())
        except ValueError:
            label_status_atualizar.configure(text="digite uma idade valida (apenas numeros)")
            return
        
        email_novo = entry_novo_email.get()
        telefone_novo = entry_novo_telefone.get()

        try:
            cursor.execute(
                "UPDATE registros SET nome = ?, idade = ?, email = ?, telefone = ? WHERE id = ?", 
                (nome_novo, idade_nova, email_novo, telefone_novo, id_confirmar["valor"]))
            conexao.commit()
            label_status_atualizar.config(text="cadastro atualizado")
        except sqlite3.IntegrityError:
            label_status_atualizar.config(text="email ja cadastrado")

    ctk.CTkButton(frame, text="buscar id", command=confirmar_id).pack(pady=5)       
    ctk.CTkButton(frame, text="salvar alteracoes", command=salvar_alteracoes).pack(pady=5)
    ctk.CTkButton(frame, text="fechar", command=lambda: esconder_overlay("atualizar cadastro")).pack(pady=5)  


def remover_usuario(id_usuario):
    cursor.execute("DELETE FROM registros WHERE id = ?", (id_usuario,))
    conexao.commit()
    
def cria_overlay_remover_usuario():
    frame = ctk.CTkFrame(janela)
    overlays["remover usuario"] = frame


    ctk.CTkLabel(frame, text="digite o id do usuario que deseja remover").pack()
    
    
    entry_id = ctk.CTkEntry(frame)
    entry_id.pack() 

    label_status_remover = ctk.CTkLabel(frame, text="")
    label_status_remover.pack()



    def confirmar_remocao():
        try:
            id_usuario = int(entry_id.get())
        except ValueError:
            label_status_remover.config(text="digite apenas o id(numero)")
            return

        cursor.execute("DELETE FROM registros WHERE id = ?", (id_usuario,))
        if cursor.fetchone() is None:
            label_status_remover.config(text="esse id nao existe")
            return
        remover_usuario(id_usuario)
        label_status_remover.config(text="usuario removido")
        conexao.commit()

    

    
    ctk.CTkButton(frame, text="remover usuario", command=confirmar_remocao).pack(pady=2)
    ctk.CTkButton(frame, text="fechar", command=lambda: esconder_overlay("remover usuario")).pack(pady=2)

def criar_overlay_cadastrar():
    frame = ctk.CTkFrame(janela)
    overlays["cadastrar"] = frame

    label_status_cadastrar = ctk.CTkLabel(frame, text="")
    label_status_cadastrar.pack()

    ctk.CTkLabel(frame, text="Nome").pack()
    entry_nome = ctk.CTkEntry(frame)
    entry_nome.pack()

    ctk.CTkLabel(frame, text="Idade").pack()
    entry_idade = ctk.CTkEntry(frame)
    entry_idade.pack()

    ctk.CTkLabel(frame, text="Email").pack()
    entry_email = ctk.CTkEntry(frame)
    entry_email.pack()

    ctk.CTkLabel(frame, text="Telefone").pack()
    entry_telefone = ctk.CTkEntry(frame)
    entry_telefone.pack()

    def cadastros():
        nome = entry_nome.get()
        try:
            idade = int(entry_idade.get())
        except ValueError:
            label_status.config(text="idade invalida")
            return
        email = entry_email.get()
        telefone = entry_telefone.get()
        try:
            cursor.execute("INSERT INTO registros (nome, idade, email, telefone) VALUES (?, ?, ?, ?)", (nome, idade, email, telefone,))
            conexao.commit()
            label_status_cadastrar.configure(text="usuario cadastrado")
        except sqlite3.IntegrityError:
            label_status_cadastrar.configure(text="email ja cadastrado")



    ctk.CTkButton(frame, text="cadastrar", command=cadastros).pack(padx=10, pady=5)
    ctk.CTkButton(frame, text="fechar", command=lambda: esconder_overlay("cadastrar")).pack(padx=10, pady=5)

def exibir_usuario():
    global tree_usuario

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", background="#2a2d2e", foreground="white", borderwidth=0)
    style.configure("Treeview", background="#292929", foreground="white", fieldbackground="#292929", borderwidth=0)
    style.map("Treeview", background=[('selected', '#3a3a3a')])

    
    if tree_usuario is None:
        colunas = ("ID", "NOME", "IDADE", "EMAIL", "TELEFONE")
        tree_usuario = ttk.Treeview(janela, columns=colunas, show="headings")
        for col in colunas:
            tree_usuario.heading(col, text=col)
        tree_usuario.pack(fill=tk.BOTH, expand=True)
        
    tree_usuario.delete(*tree_usuario.get_children())
    cursor.execute("SELECT * FROM registros ORDER BY nome ASC")
    for linha in cursor.fetchall():
        tree_usuario.insert("", tk.END, values=linha)

    tree_usuario.pack(padx=20, pady=20, fill="both", expand=True)



def ao_fechar():
    conexao.commit()
    conexao.close()
    janela.destroy()
    

#=================================JANELA PRINCIPAL=========================================================
left_sidebar = ctk.CTkFrame(janela, width=200,corner_radius=0, height=200)
left_sidebar.pack(side="right", fill="y", pady=0, padx=0)
nome_left_sidebar = ctk.CTkLabel(left_sidebar, text="CADASTRO DE PRODUTOS", font=("Arial", 20, "bold"))
nome_left_sidebar.pack(pady=20, padx=(20, 30))

sidebar_frame = ctk.CTkFrame(janela, width=200,corner_radius=0, height=200)
sidebar_frame.pack(side="left", fill="y", pady=0, padx=0)
nome_sidebar = ctk.CTkLabel(sidebar_frame, text="MENU DE USUSARIOS", font=("Arial", 20, "bold"))
nome_sidebar.pack(pady=20, padx=(20, 30))


ctk.CTkButton(sidebar_frame, text="cadastrar", image=icone_add, compound="left", command=lambda: mostrar_overlay("cadastrar")).pack(padx=10, pady=2)
label_status = ctk.CTkLabel(janela, text="")
label_status.pack()

ctk.CTkButton(sidebar_frame, text="atualizar cadastro",image=icone_user_add, command=lambda: mostrar_overlay("atualizar cadastro")).pack(padx=10, pady=2)
label_status = ctk.CTkLabel(janela, text="")
label_status.pack()

botao_remover = ctk.CTkButton(sidebar_frame, text="remover usuario", image=icone_delete_user, command=lambda: mostrar_overlay("remover usuario")).pack(padx=10, pady=2)
label_status = ctk.CTkLabel(janela, text="")
label_status.pack()

ctk.CTkButton(sidebar_frame, text="exibir usuarios", image=icone_list_user, command=exibir_usuario).pack(padx=10, pady=2)
label_status = ctk.CTkLabel(janela, text="")
label_status.pack()

ctk.CTkButton(left_sidebar, text="cadastrar produto", command=add_de_produtos).pack(padx=10, pady=1)
label_status = ctk.CTkLabel(left_sidebar, text="")
label_status.pack()

ctk.CTkButton(left_sidebar, text="remover produto", command=lambda: mostrar_overlay("remover produto")).pack(padx=10, pady=2)
label_status = ctk.CTkLabel(left_sidebar, text="")
label_status.pack()

ctk.CTkButton(sidebar_frame, text="sair", image=icone_sair, command=janela.destroy).pack(padx=10, pady=100)
label_status = ctk.CTkLabel(janela, text="")
label_status.pack()


criar_overlay_cadastrar()
criar_overlay_atualizar_cadastro()
cria_overlay_remover_usuario()
cria_overlay_remover_produto()



janela.protocol("WM_DELETE_WINDOW", ao_fechar)
janela.mainloop()
