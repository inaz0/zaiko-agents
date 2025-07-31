INSTALLATEUR POWERSHELL AVEC FENÊTRE GUI ET TÂCHE PLANIFIÉE

1. Pré-requis
   - Python 3.7+
   - pip
   - PyInstaller (installer avec: pip install pyinstaller)

2. Compilation en .exe
   Depuis le dossier InstallateurScript, lancez :

   pyinstaller --onefile --noconsole --add-data "listApplication.ps1;." agent_windows_zaiko_0.0.1.py

3. Fichier de sortie :
   - ./dist/agent_windows_zaiko_0.0.1.exe

4. Comportement :
   - Ouvre une interface graphique
   - Demande deux variables utilisateur
   - Écrit dans un fichier .env dans ProgramData
   - Copie le listApplication.ps1 dans ProgramData
   - Crée une tâche planifiée Windows (exécution quotidienne)

5. Conseils :
   - Exécuter le .exe en tant qu’**Administrateur**
   - Modifier `listApplication.ps1` selon vos besoins métiers
