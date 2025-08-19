import os
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox
import sys
import ctypes

# === Configuration ===
APP_FOLDER = r"C:\ProgramData\CyberFacile\Zaiko"
SCRIPT_NAME = "listApplication.ps1"
ENV_FILE = ".env"
VBS_FILE = "run_silent.vbs"
TASK_NAME = "ZAIKO - CyberFacile - DailyScript"

# === Fonctions ===

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def ensure_directory():
    if not os.path.exists(APP_FOLDER):
        os.makedirs(APP_FOLDER)

def copy_script():
    source_path = get_resource_path(SCRIPT_NAME)
    dest_path = os.path.join(APP_FOLDER, SCRIPT_NAME)
    with open(source_path, "r") as src, open(dest_path, "w") as dst:
        dst.write(src.read())

def write_env(var1, var2):
    env_path = os.path.join(APP_FOLDER, ENV_FILE)
    with open(env_path, "w") as f:
        f.write("DESTINATION_URL=https://zaiko.cyber-facile.fr/api/applications\n")
        f.write(f"CLIENT_ID={var1}\n")
        f.write(f"SECRET={var2}\n")

def create_vbs_launcher():
    vbs_path = os.path.join(APP_FOLDER, VBS_FILE)
    ps_path = os.path.join(APP_FOLDER, SCRIPT_NAME)
    with open(vbs_path, "w") as vbs:
        vbs.write('Set WshShell = CreateObject("Wscript.Shell")\n')
        vbs.write(f'WshShell.Run "powershell.exe -ExecutionPolicy Bypass -File ""{ps_path}""", 0, False\n')
    return vbs_path

def task_exists(task_name):
    result = subprocess.run(["schtasks", "/Query", "/TN", task_name], capture_output=True, text=True)
    return result.returncode == 0

def delete_scheduled_task():
    if task_exists(TASK_NAME):
        subprocess.run([
            "schtasks", "/Delete",
            "/TN", TASK_NAME,
            "/F"
        ], capture_output=True)

def create_scheduled_task():
    if task_exists(TASK_NAME):
        messagebox.showinfo("Info", f"La tâche '{TASK_NAME}' existe déjà.")
        return

    vbs_path = create_vbs_launcher()
    command = f'wscript.exe "{vbs_path}"'
    result = subprocess.run([
        "schtasks", "/Create",
        "/SC", "ONSTART",
        "/TN", TASK_NAME,
        "/TR", command,
        "/RL", "HIGHEST",
        "/F"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Erreur lors de la création de la tâche planifiée :\n{result.stderr.strip()}")

# === Programme principal ===

def main():
    if not is_admin():
        tk.Tk().withdraw()
        messagebox.showerror("Droits requis", "Ce programme doit être exécuté en tant qu'administrateur.")
        sys.exit(1)

    root = tk.Tk()
    root.withdraw()

    var1 = simpledialog.askstring("Configuration", "Entrez le CLIENT_ID :")
    var2 = simpledialog.askstring("Configuration", "Entrez le SECRET :")

    if not var1 or not var2:
        messagebox.showerror("Erreur", "Les deux valeurs sont obligatoires.")
        return

    try:
        ensure_directory()
        copy_script()
        write_env(var1, var2)
        delete_scheduled_task()
        create_scheduled_task()
        messagebox.showinfo("Succès", "Installation réussie. Le script sera exécuté une fois par jour en mode totalement silencieux.")
    except Exception as e:
        messagebox.showerror("Échec", str(e))

if __name__ == "__main__":
    main()
