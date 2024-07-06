import os
import subprocess
import json
from tkinter import *
from tkinter import filedialog
import psutil

# Dossier pour stocker les sauvegardes
save_folder = "saved_shortcuts"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Fonction pour charger les données sauvegardées pour un raccourci spécifique
def load_shortcut_data(shortcut_name):
    shortcut_file = os.path.join(save_folder, f"{shortcut_name}.json")
    if os.path.exists(shortcut_file):
        with open(shortcut_file, 'r') as f:
            return json.load(f)
    return {}

# Fonction pour sauvegarder les données pour un raccourci spécifique
def save_shortcut_data(shortcut_name, data):
    shortcut_file = os.path.join(save_folder, f"{shortcut_name}.json")
    with open(shortcut_file, 'w') as f:
        json.dump(data, f)

# Fonction pour charger toutes les données sauvegardées au démarrage
def load_all_saved_data():
    global shortcuts
    shortcuts = []

    for file_name in os.listdir(save_folder):
        if file_name.endswith(".json"):
            shortcut_name = os.path.splitext(file_name)[0]
            shortcut_data = load_shortcut_data(shortcut_name)
            if 'py_file' in shortcut_data and 'batch_content' in shortcut_data:
                shortcuts.append((shortcut_data['py_file'], shortcut_name, shortcut_data['batch_content']))

# Fonction pour sauvegarder les données à la fermeture de l'application
def save_all_data_on_exit():
    for py_file, shortcut_name, batch_content in shortcuts:
        shortcut_data = {
            'py_file': py_file,
            'batch_content': batch_content
        }
        save_shortcut_data(shortcut_name, shortcut_data)

# Fonction pour quitter l'application
def quit_application():
    save_all_data_on_exit()
    main_window.destroy()

# Fonction pour réduire la fenêtre CMD lors de l'exécution du fichier .py
def execute_py_file(py_file):
    cmd_command = f'cmd /c start /min cmd.exe /K "cd {os.path.dirname(py_file)} && python \"{py_file}\""'
    subprocess.Popen(cmd_command, shell=True)

# Exécuter une commande CMD minimisée dès l'ouverture de l'application
def run_minimized_cmd_on_startup():
    cmd_command = 'cmd /c start /min cmd.exe'
    subprocess.Popen(cmd_command, shell=True)

# Fonction pour changer la taille de la police d'écriture
def change_font_size(size):
    global current_font_size
    current_font_size = size
    main_window.option_add('*Font', f'Arial {current_font_size}')

# Couleurs de fond disponibles
background_colors = {
    'default': '#312b41',
    'white': 'white',
    'black': 'black',
    'blue': 'blue',
    'red': 'red',
    'green': 'green'
}

# Fonction pour changer la couleur de fond de toute l'application
def change_background_color(color):
    main_window.configure(bg=background_colors.get(color, '#312b41'))  # Default to dark theme if color not found

# Fonction pour fermer tous les CMD sauf celui de l'application
def close_other_cmd_windows():
    current_pid = os.getpid()  # PID de l'application en cours
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'cmd.exe' and proc.pid != current_pid:
            proc.terminate()  # Terminer les processus CMD sauf celui de l'application

# Fonction pour afficher le texte "Created by Soniceurs" en bas à droite
def show_created_by_label():
    created_by_label = Label(main_window, text="Created by Soniceurs", fg='white', bg='#312b41', font=('Arial', 10))
    created_by_label.pack(side=BOTTOM, padx=10, pady=10)

# Fonction pour afficher le cadre principal (page d'accueil)
def show_home_frame():
    clear_current_frame()
    refresh_home_frame()
    hide_return_button()

# Fonction pour afficher le bouton "Return to Selection"
def show_return_button():
    return_button.pack(side=RIGHT, padx=10, pady=10)

# Fonction pour cacher le bouton "Return to Selection"
def hide_return_button():
    return_button.pack_forget()

# Fonction pour sauvegarder le renommage d'un raccourci
def save_renamed_shortcut(rename_entry, current_name):
    new_name = rename_entry.get()
    if new_name.strip() and new_name != current_name:
        for i, (py_file, shortcut_name, batch_content) in enumerate(shortcuts):
            if shortcut_name == current_name:
                update_shortcut_data(current_name, batch_content)  # Mettre à jour le contenu du script batch
                shortcuts[i] = (py_file, new_name, batch_content)
                refresh_home_frame()
                break

# Fonction pour supprimer un raccourci
def delete_shortcut(shortcut_name):
    global shortcuts
    for i, (py_file, name, _) in enumerate(shortcuts):
        if name == shortcut_name:
            del shortcuts[i]
            break
    refresh_home_frame()

# Fonction pour effacer le cadre actuel
def clear_current_frame():
    for widget in current_frame.winfo_children():
        widget.destroy()

# Fonction pour sélectionner un fichier .py et créer un raccourci
def select_py_file_and_create_shortcut():
    py_file = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    if py_file:
        create_shortcut(py_file)

# Fonction pour créer un raccourci sur la page d'accueil
def create_shortcut(py_file):
    shortcut_name = os.path.basename(py_file)
    shortcuts.append((py_file, shortcut_name, ""))  # Ajout d'une chaîne vide pour le contenu du script batch initial
    refresh_home_frame()

# Fonction pour rafraîchir le cadre principal (page d'accueil)
def refresh_home_frame():
    clear_current_frame()
    for py_file, shortcut_name, _ in shortcuts:
        shortcut_frame = Frame(current_frame, bg='#312b41')
        shortcut_frame.pack(pady=10, padx=10, fill=X)
        select_button = Button(shortcut_frame, text="Select", command=lambda pf=py_file, sn=shortcut_name: select_shortcut(pf, sn), fg='dark blue', font=('Arial', 12))
        select_button.pack(side=LEFT, padx=10)
        shortcut_label = Label(shortcut_frame, text=f"Shortcut: {shortcut_name}", fg='white', bg='#312b41', font=('Arial', 12))
        shortcut_label.pack(side=LEFT)
        rename_entry = Entry(shortcut_frame, width=20, font=('Arial', 12))
        rename_entry.insert(0, shortcut_name)
        rename_entry.pack(side=LEFT, padx=10)
        save_button = Button(shortcut_frame, text="Save", command=lambda re=rename_entry, sn=shortcut_name: save_renamed_shortcut(re, sn), fg='dark blue', font=('Arial', 12))
        save_button.pack(side=LEFT, padx=5)
        trash_button = Button(shortcut_frame, text="Trash", command=lambda sn=shortcut_name: delete_shortcut(sn), fg='dark blue', font=('Arial', 12))
        trash_button.pack(side=LEFT, padx=5)

# Fonction pour sélectionner un raccourci et afficher ses détails
def select_shortcut(py_file, shortcut_name):
    clear_current_frame()
    selected_label = Label(current_frame, text=f"Selected Shortcut: {shortcut_name}", fg='white', bg='#312b41', font=('Arial', 14, 'bold'))
    selected_label.pack(pady=10)
    batch_text = Text(current_frame, height=5, width=85, font=('Arial', 12))
    batch_text.insert("1.0", f"@echo off\npython \"{py_file}\"")
    batch_text.pack(pady=5)
    edit_batch_button = Button(current_frame, text="Load Batch Script", command=lambda bt=batch_text: load_batch_script(bt, shortcut_name), fg='dark blue', font=('Arial', 12))
    edit_batch_button.pack(pady=5)
    execute_button = Button(current_frame, text="Execute", command=lambda pf=py_file: execute_py_file(pf), fg='dark blue', font=('Arial', 12))
    execute_button.pack(pady=10)
    show_return_button()

# Fonction pour charger un script batch existant
def load_batch_script(batch_text, shortcut_name):
    batch_file = filedialog.askopenfilename(filetypes=[("Batch files", "*.bat")])
    if batch_file:
        with open(batch_file, 'r') as f:
            batch_content = f.read()
            batch_text.delete("1.0", END)
            batch_text.insert("1.0", batch_content)
            update_shortcut_data(shortcut_name, batch_content)

# Fonction pour mettre à jour les données d'un raccourci avec le contenu du script batch
def update_shortcut_data(shortcut_name, batch_content):
    for i, (py_file, name, _) in enumerate(shortcuts):
        if name == shortcut_name:
            shortcuts[i] = (py_file, shortcut_name, batch_content)
            break

# Fenêtre principale Tkinter
main_window = Tk()
main_window.geometry('800x720')  
main_window.title('Multi Execution Python')
main_window.configure(bg='#312b41')

# Barre de navigation
nav_frame = Frame(main_window, bg='#312b41')
nav_frame.pack(side=TOP, fill=X)

# Cadre principal pour changer les pages
current_frame = Frame(main_window, bg='#312b41')
current_frame.pack(expand=1, fill=BOTH)

# Bouton "Return to Selection"
return_button = Button(nav_frame, text="Return to Selection", command=lambda: show_home_frame(), fg='dark blue', font=('Arial', 14, 'bold'))
return_button.pack(side=RIGHT, padx=10, pady=10)
return_button.pack_forget()  # Cacher le bouton au démarrage

# Bouton "Quit"
quit_button = Button(nav_frame, text="Quit", command=quit_application, fg='dark blue', font=('Arial', 14, 'bold'))
quit_button.pack(side=LEFT, padx=10, pady=10)

# Bouton pour afficher la page de gestion des fichiers .py et créer un raccourci
manage_py_button = Button(nav_frame, text="Create Shortcut Python", command=select_py_file_and_create_shortcut, fg='dark blue', font=('Arial', 14, 'bold'))
manage_py_button.pack(side=LEFT, padx=10, pady=10)

# Bouton pour fermer tous les CMD sauf celui de l'application
close_cmd_button = Button(main_window, text="Close All CMD", command=close_other_cmd_windows, fg='dark blue', font=('Arial', 14, 'bold'))
close_cmd_button.pack(side=BOTTOM, pady=10)

# Fonction pour afficher le texte "Created by Soniceurs" en bas à droite
show_created_by_label()

# Charger les données sauvegardées au démarrage
load_all_saved_data()

# Afficher les raccourcis existants sur la page d'accueil au démarrage
refresh_home_frame()

# Gestion de la fermeture de l'application
main_window.protocol("WM_DELETE_WINDOW", quit_application)

# Boucle principale de l'application Tkinter
main_window.mainloop()
