import winreg
import sys
import os

# Fájlnevek (ha máshogy nevezted el őket, itt írd át!)
szerkeszto_fajl = "magyarkod_szerkeszto.py"
ikon_fajl = "ikon.ico"

# Lekérjük a teljes, pontos útvonalakat
python_exe = sys.executable
# A pythonw.exe-t használjuk, hogy ne ugorjon fel fekete terminál ablak a háttérben
pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")

script_utvonal = os.path.abspath(szerkeszto_fajl)
ikon_utvonal = os.path.abspath(ikon_fajl)

# A parancs, ami dupla kattintáskor lefut
parancs = f'"{pythonw_exe}" "{script_utvonal}" "%1"'

try:
    # 1. Kiterjesztés összekötése egy azonosítóval
    winreg.SetValue(winreg.HKEY_CURRENT_USER, r"Software\Classes\.mkod", winreg.REG_SZ, "MagyarKod.File")

    # 2. Az azonosító beállítása (Név és Ikon)
    kulcs = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\MagyarKod.File")
    winreg.SetValue(kulcs, "", winreg.REG_SZ, "MagyarKód Program")

    ikon_kulcs = winreg.CreateKey(kulcs, "DefaultIcon")
    winreg.SetValue(ikon_kulcs, "", winreg.REG_SZ, f'"{ikon_utvonal}"')

    # 3. Megnyitási parancs beállítása (Dupla kattintás)
    parancs_kulcs = winreg.CreateKey(kulcs, r"shell\open\command")
    winreg.SetValue(parancs_kulcs, "", winreg.REG_SZ, parancs)

    print("Sikeresen beállítva! Mostantól az .mkod fájlok a szerkesztőddel nyílnak meg.")
except Exception as e:
    print("Hiba történt:", e)