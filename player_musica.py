import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import os
import random
import mutagen.mp3

pygame.mixer.init()

playlist = []
indice_atual = 0
modo_aleatorio = False
loop_playlist = True
tocando = False
duracao_musica = 0

def carregar_musicas():
    global playlist
    arquivos = filedialog.askopenfilenames(filetypes=[("Arquivos de áudio", "*.mp3 *.wav")])
    if arquivos:
        novos_arquivos = [f for f in arquivos if f not in playlist]
        playlist.extend(novos_arquivos)
        atualizar_lista()
    else:
        messagebox.showinfo("Informação", "Nenhuma música selecionada.")

def atualizar_lista():
    lista_musicas.delete(0, tk.END)
    for musica in playlist:
        lista_musicas.insert(tk.END, os.path.basename(musica))
    if playlist:
        lista_musicas.select_clear(0, tk.END)
        lista_musicas.select_set(indice_atual)
        lista_musicas.activate(indice_atual)

def tocar_musica(indice):
    global indice_atual, duracao_musica, tocando
    if not playlist:
        messagebox.showwarning("Aviso", "A playlist está vazia!")
        return
    if 0 <= indice < len(playlist):
        try:
            pygame.mixer.music.load(playlist[indice])
            pygame.mixer.music.play()
            nome = os.path.basename(playlist[indice])
            label_musica.config(text=f"Tocando: {nome}")
            indice_atual = indice
            tocando = True
            atualizar_lista()

            audio = mutagen.mp3.MP3(playlist[indice])
            duracao_musica = int(audio.info.length)
            barra_progresso['maximum'] = duracao_musica
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao tocar música:\n{e}")
            duracao_musica = 0
            barra_progresso['maximum'] = 100
    else:
        messagebox.showerror("Erro", "Índice inválido.")

def tocar_proxima():
    global indice_atual
    if not playlist:
        messagebox.showwarning("Aviso", "A playlist está vazia!")
        return
    if modo_aleatorio:
        indice_atual = random.randint(0, len(playlist) - 1)
    else:
        indice_atual = (indice_atual + 1) % len(playlist)
    tocar_musica(indice_atual)

def tocar_anterior():
    global indice_atual
    if not playlist:
        messagebox.showwarning("Aviso", "A playlist está vazia!")
        return
    indice_atual = (indice_atual - 1) % len(playlist)
    tocar_musica(indice_atual)

def pausar_ou_retomar():
    global tocando
    if pygame.mixer.music.get_busy() and tocando:
        pygame.mixer.music.pause()
        tocando = False
    else:
        pygame.mixer.music.unpause()
        tocando = True

def alternar_modo(tipo):
    global modo_aleatorio, loop_playlist
    if tipo == "aleatorio":
        modo_aleatorio = not modo_aleatorio
        btn_shuffle.config(text="🔀 Aleatório: On" if modo_aleatorio else "🔀 Aleatório: Off")
    elif tipo == "loop":
        loop_playlist = not loop_playlist
        btn_loop.config(text="🔁 Loop: On" if loop_playlist else "🔁 Loop: Off")

def ajustar_volume(val):
    volume = float(val) / 100
    pygame.mixer.music.set_volume(volume)

def atualizar_tempo():
    if tocando and duracao_musica > 0:
        pos = pygame.mixer.music.get_pos() // 1000
        if pos > duracao_musica:
            pos = duracao_musica
        barra_progresso['value'] = pos
        tempo_atual.config(text=segundos_para_tempo(pos))
        tempo_total.config(text=segundos_para_tempo(duracao_musica))
        if pos >= duracao_musica - 1:
            if loop_playlist:
                tocar_proxima()
    root.after(1000, atualizar_tempo)

def segundos_para_tempo(segundos):
    m, s = divmod(segundos, 60)
    return f"{m:02d}:{s:02d}"

def quando_musica_terminar():
    if not pygame.mixer.music.get_busy() and tocando:
        if loop_playlist:
            tocar_proxima()
    root.after(1000, quando_musica_terminar)

def selecionar_musica(event):
    selecao = lista_musicas.curselection()
    if selecao:
        indice = selecao[0]
        tocar_musica(indice)

# --- Interface ---

root = tk.Tk()
root.title("MusiQ 🎵")
root.geometry("600x450")
root.configure(bg="#1e1e1e")

# Cabeçalho com nome estilizado
label_titulo = tk.Label(root, text="🎶 MusiQ Player", font=("Segoe UI", 20, "bold"), fg="#ff8000", bg="#1e1e1e")
label_titulo.pack(pady=(10, 5))

label_musica = tk.Label(root, text="Nenhuma música tocando", bg="#1e1e1e", fg="white", font=("Segoe UI", 12))
label_musica.pack(pady=(0, 10))

frame_main = tk.Frame(root, bg="#1e1e1e")
frame_main.pack(fill="both", expand=True, padx=10, pady=(0,10))

lista_musicas = tk.Listbox(frame_main, bg="#2b2b2b", fg="white", selectbackground="#ff8000", height=15)
lista_musicas.pack(side="left", fill="both", expand=True)
lista_musicas.bind("<<ListboxSelect>>", selecionar_musica)

scroll = ttk.Scrollbar(frame_main, orient="vertical", command=lista_musicas.yview)
scroll.pack(side="left", fill="y")
lista_musicas.config(yscrollcommand=scroll.set)

frame_controles = tk.Frame(frame_main, bg="#1e1e1e")
frame_controles.pack(side="right", fill="y", padx=20)

btn_anterior = ttk.Button(frame_controles, text="⏮️ Anterior", command=tocar_anterior, style="Estilo.TButton", width=15)
btn_play = ttk.Button(frame_controles, text="⏯️ Pausar/Continuar", command=pausar_ou_retomar, style="Estilo.TButton", width=15)
btn_proxima = ttk.Button(frame_controles, text="⏭️ Próxima", command=tocar_proxima, style="Estilo.TButton", width=15)
btn_loop = ttk.Button(frame_controles, text="🔁 Loop: On", command=lambda: alternar_modo("loop"), style="Estilo.TButton", width=15)
btn_shuffle = ttk.Button(frame_controles, text="🔀 Aleatório: Off", command=lambda: alternar_modo("aleatorio"), style="Estilo.TButton", width=15)
btn_carregar = ttk.Button(frame_controles, text="🎵 Carregar Músicas", command=carregar_musicas, style="Estilo.TButton", width=15)

btn_anterior.pack(pady=5)
btn_play.pack(pady=5)
btn_proxima.pack(pady=5)
btn_loop.pack(pady=5)
btn_shuffle.pack(pady=5)
btn_carregar.pack(pady=20)

frame_tempo = tk.Frame(frame_controles, bg="#1e1e1e")
frame_tempo.pack(pady=10, fill='x')

tempo_atual = tk.Label(frame_tempo, text="00:00", bg="#1e1e1e", fg="white", font=("Segoe UI", 10))
tempo_atual.pack(side='left')

barra_progresso = ttk.Progressbar(frame_tempo, length=200, mode='determinate')
barra_progresso.pack(side='left', padx=5)

tempo_total = tk.Label(frame_tempo, text="00:00", bg="#1e1e1e", fg="white", font=("Segoe UI", 10))
tempo_total.pack(side='left')

frame_volume = tk.Frame(frame_controles, bg="#1e1e1e")
frame_volume.pack(pady=10)

label_volume = tk.Label(frame_volume, text="🔊 Volume", bg="#1e1e1e", fg="white", font=("Segoe UI", 10))
label_volume.pack(side='left', padx=5)

slider_volume = ttk.Scale(frame_volume, from_=0, to=100, orient='horizontal', command=ajustar_volume)
slider_volume.set(70)
pygame.mixer.music.set_volume(0.7)
slider_volume.pack(side='left')

style = ttk.Style()
style.theme_use("clam")
style.configure("Estilo.TButton",
                font=("Segoe UI", 10),
                padding=6)

style.map("Estilo.TButton",
          foreground=[('!disabled', 'white')],
          background=[('!disabled', '#333333'), ('active', '#ff8000')])

atualizar_tempo()
quando_musica_terminar()

root.mainloop()
