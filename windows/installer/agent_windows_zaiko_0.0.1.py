import os
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox
import sys
import ctypes
import win32crypt

# === Configuration ===
APP_FOLDER = r"C:\ProgramData\CyberFacile\Zaiko"
SCRIPT_NAME = "listApplication.ps1"
ENV_FILE = ".env"
SECRET_FILE = "secret.bin"
TASK_NAME = "ZAIKO - CyberFacile - DailyScript"

# === Fonctions système ===

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

def write_env(var1):
    env_path = os.path.join(APP_FOLDER, ENV_FILE)
    with open(env_path, "w") as f:
        f.write(f"DESTINATION_URL=zaiko.cyber-facile.fr\n")
        f.write(f"CLIENT_ID={var1}\n")

def write_encrypted_secret(secret):
    encrypted = win32crypt.CryptProtectData(
        secret.encode("utf-8"),
        "description", None, None, None, 0
    )
    secret_path = os.path.join(APP_FOLDER, SECRET_FILE)
    with open(secret_path, "wb") as f:
        f.write(encrypted)


def task_exists(task_name):
    result = subprocess.run(["schtasks", "/Query", "/TN", task_name], capture_output=True, text=True)
    return result.returncode == 0

def create_scheduled_task():
    if task_exists(TASK_NAME):
        messagebox.showinfo("Info", f"La tâche '{TASK_NAME}' existe déjà.")
        return

    script_path = os.path.join(APP_FOLDER, SCRIPT_NAME)
    command = f'powershell.exe -ExecutionPolicy Bypass -File "{script_path}"'
    result = subprocess.run([
        "schtasks", "/Create",
        "/SC", "DAILY",
        "/TN", TASK_NAME,
        "/TR", command,
        "/ST", "10:00",
        "/RL", "HIGHEST",
        "/F"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Erreur lors de la création de la tâche planifiée :\n{result.stderr.strip()}")

# === Interface graphique ===

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
        write_env(var1)
        write_encrypted_secret(var2)
        create_scheduled_task()
        messagebox.showinfo("Succès", "Installation réussie. Le script sera exécuté chaque jour à 10h.")
    except Exception as e:
        messagebox.showerror("Échec", str(e))

if __name__ == "__main__":
    main()
