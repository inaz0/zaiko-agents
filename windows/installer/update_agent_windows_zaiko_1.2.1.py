import os
import subprocess
import sys
import ctypes
import tkinter as tk
from tkinter import messagebox

# === Config ===
APP_FOLDER = r"C:\ProgramData\CyberFacile\Zaiko"
SCRIPT_NAME = "listApplication.ps1"
VBS_FILE = "run_silent.vbs"
TASK_NAME = "ZAIKO - CyberFacile - DailyScript"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def copy_script():
    source_path = get_resource_path(SCRIPT_NAME)
    dest_path = os.path.join(APP_FOLDER, SCRIPT_NAME)
    with open(source_path, "r") as src, open(dest_path, "w") as dst:
        dst.write(src.read())

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
    vbs_path = create_vbs_launcher()
    command = f'wscript.exe "{vbs_path}"'
    result = subprocess.run([
        "schtasks", "/Create",
        "/SC", "ONLOGON",
        "/TN", TASK_NAME,
        "/TR", command,
        "/RL", "HIGHEST",
        "/F",
        "/RU",  os.getlogin()
    ], capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Erreur création tâche : {result.stderr.strip()}")

def set_task_conditions():
    try:
        ps_script = f'''
        $task = Get-ScheduledTask -TaskName "{TASK_NAME}"
        $settings = $task.Settings

        # Désactiver les contraintes liées à la batterie
        $settings.DisallowStartIfOnBatteries = $false
        $settings.StopIfGoingOnBatteries = $false

        # Appliquer les nouveaux paramètres
        Set-ScheduledTask -TaskName "{TASK_NAME}" -Settings $settings
        '''
        subprocess.run(["powershell.exe", "-Command", ps_script], capture_output=True)
    except Exception as e:
        print(f"[⚠] Impossible de modifier les conditions d'alimentation : {e}")


def main():
    if not is_admin():
        tk.Tk().withdraw()
        messagebox.showerror("Droits requis", "Ce programme doit être exécuté en tant qu'administrateur.")
        sys.exit(1)

    tk.Tk().withdraw()
    confirm = messagebox.askyesno(
        title="Mise à jour",
        message="Voulez-vous appliquer la mise à jour du script et de la tâche planifiée ?"
    )

    if not confirm:
        messagebox.showinfo("Annulé", "La mise à jour a été annulée par l'utilisateur.")
        sys.exit(0)

    try:
        copy_script()
        delete_scheduled_task()
        create_scheduled_task()
        set_task_conditions()
        messagebox.showinfo("Succès", "✅ Mise à jour appliquée avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", f"❌ Erreur lors de la mise à jour :\n{str(e)}")

if __name__ == "__main__":
    main()
