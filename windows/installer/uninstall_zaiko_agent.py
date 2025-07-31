import os
import subprocess
import shutil
import tkinter as tk
from tkinter import messagebox
import sys
import ctypes

# === Configuration ===
APP_FOLDER = r"C:\ProgramData\CyberFacile\Zaiko"
TASK_NAME = "ZAIKO - CyberFacile - DailyScript"

# === Fonctions ===

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def delete_scheduled_task():
    result = subprocess.run([
        "schtasks", "/Delete",
        "/TN", TASK_NAME,
        "/F"
    ], capture_output=True, text=True)

    if result.returncode != 0 and "ERROR: The system cannot find the file specified." not in result.stderr:
        raise Exception(f"Erreur lors de la suppression de la tâche planifiée :\n{result.stderr.strip()}")

def delete_install_folder():
    if os.path.exists(APP_FOLDER):
        shutil.rmtree(APP_FOLDER)

# === Exécution principale ===

def main():
    if not is_admin():
        tk.Tk().withdraw()
        messagebox.showerror("Droits requis", "Ce programme doit être exécuté en tant qu'administrateur.")
        sys.exit(1)

    try:
        delete_scheduled_task()
        delete_install_folder()
        tk.Tk().withdraw()
        messagebox.showinfo("Désinstallation", "Le logiciel a été supprimé avec succès.")
    except Exception as e:
        tk.Tk().withdraw()
        messagebox.showerror("Erreur", str(e))

if __name__ == "__main__":
    main()
