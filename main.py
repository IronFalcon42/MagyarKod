import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import io
import contextlib
import re
import random
import time
import os
import shutil  # <-- ÚJ: Ez felel a fájlok másolásáért!

try:
    import pygame
except ImportError:
    pygame = None

pg_allapot = {"screen": None, "clock": None}


# --- Pygame Motor Függvények ---
def mk_ablak_meret(szelesseg, magassag):
    if not pygame: raise Exception("A pygame nincs telepítve! Futtasd: pip install pygame")
    pygame.init()
    pg_allapot["screen"] = pygame.display.set_mode((szelesseg, magassag))
    pg_allapot["clock"] = pygame.time.Clock()
    pygame.display.set_caption("MagyarKód - Pygame Játék")


def mk_hatterszin(r, g, b):
    if pg_allapot["screen"]: pg_allapot["screen"].fill((r, g, b))


def mk_teglalap(x, y, szelesseg, magassag, r, g, b):
    if pg_allapot["screen"]:
        pygame.draw.rect(pg_allapot["screen"], (r, g, b), pygame.Rect(x, y, szelesseg, magassag))


def mk_kep_betoltes(fajlnev, szelesseg, magassag):
    if not pygame: return None
    try:
        if not os.path.exists(fajlnev):
            print(f"HIBA: Nem találom a '{fajlnev}' képet!")
            return None
        kep = pygame.image.load(fajlnev).convert_alpha()
        return pygame.transform.scale(kep, (szelesseg, magassag))
    except Exception as e:
        print(f"Hiba a kép betöltésekor: {e}")
        return None


def mk_kep_rajzolás(kep, x, y):
    if not pygame or not pg_allapot["screen"] or kep is None: return
    pg_allapot["screen"].blit(kep, (x, y))


def mk_kep_frissites(fps=60):
    if not pygame: return
    pygame.display.flip()
    if pg_allapot["clock"]: pg_allapot["clock"].tick(fps)


def mk_kilepes_kerve():
    if not pygame: return True
    for event in pygame.event.get():
        if event.type == pygame.QUIT: return True
    return False


def mk_lenyomva(gomb_nev):
    if not pygame: return False
    keys = pygame.key.get_pressed()
    gomb_szotar = {
        "fel": pygame.K_UP, "le": pygame.K_DOWN, "balra": pygame.K_LEFT, "jobbra": pygame.K_RIGHT,
        "szóköz": pygame.K_SPACE, "esc": pygame.K_ESCAPE, "w": pygame.K_w, "a": pygame.K_a, "s": pygame.K_s,
        "d": pygame.K_d
    }
    k = gomb_szotar.get(gomb_nev.lower())
    return keys[k] if k is not None else False


def mk_jatek_vege():
    if pygame: pygame.quit()


# --- JAVÍTOTT KÉP MEGNYITÁS, MÁSOLÁS ÉS ELŐNÉZET ---
def kep_megnyitasa_es_elonezet():
    fajl_utvonal = filedialog.askopenfilename(
        title="Kép megnyitása előnézethez",
        filetypes=[("Képfájlok", "*.png *.gif *.pgm *.ppm"), ("Minden fájl", "*.*")]
    )
    if not fajl_utvonal:
        return

    fajlnev = os.path.basename(fajl_utvonal)

    try:
        eredeti_kep = tk.PhotoImage(file=fajl_utvonal)
        szelesseg = eredeti_kep.width()
        magassag = eredeti_kep.height()

        elonezet_ablak = tk.Toplevel(ablak)
        elonezet_ablak.title(f"Kép előnézet - {fajlnev}")
        elonezet_ablak.geometry("420x520")
        elonezet_ablak.config(bg="#252526")

        tk.Label(elonezet_ablak, text="Kép előnézet", fg="#569CD6", bg="#252526", font=("Arial", 14, "bold")).pack(
            side=tk.TOP, pady=10)

        def beilleszt_kodba():
            # 1. KÉP ÁTMÁSOLÁSA A PROJEKT MAPPÁJÁBA
            jelenlegi_mappa = os.getcwd()
            cel_utvonal = os.path.join(jelenlegi_mappa, fajlnev)

            try:
                # Csak akkor másoljuk át, ha nem eleve ebben a mappában van!
                if os.path.abspath(fajl_utvonal) != os.path.abspath(cel_utvonal):
                    shutil.copy(fajl_utvonal, cel_utvonal)
            except Exception as e:
                messagebox.showerror("Másolási hiba", f"Nem sikerült a képet bemásolni a játék mappájába:\n{e}")
                return  # Ha hiba van a másolásnál, megszakítjuk

            # 2. KÓD GENERÁLÁSA
            valtozo_nev = os.path.splitext(fajlnev)[0].lower()
            valtozo_nev = re.sub(r'\W+', '', valtozo_nev)
            if not valtozo_nev: valtozo_nev = "kep"

            kod_sor = f'{valtozo_nev} = kép_betöltés("{fajlnev}", {szelesseg}, {magassag})\n'
            kod_szerkeszto.insert(tk.INSERT, kod_sor)
            szintaxis_kiemeles()
            elonezet_ablak.destroy()

            # Sikeres másolás jelzése
            eredmeny_doboz.config(state=tk.NORMAL)
            eredmeny_doboz.insert(tk.END, f"[Rendszer]: '{fajlnev}' sikeresen bemásolva a projekt mappájába!\n")
            eredmeny_doboz.config(state=tk.DISABLED)
            eredmeny_doboz.see(tk.END)

        gomb_frame = tk.Frame(elonezet_ablak, bg="#252526")
        gomb_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=15)

        tk.Button(
            gomb_frame,
            text="➕ Bemásolás és Beszúrás",
            bg="#4CAF50", fg="white",
            font=("Arial", 12, "bold"),
            command=beilleszt_kodba
        ).pack()

        info_szoveg = f"Fájlnév: {fajlnev}\nEredeti méret: {szelesseg} x {magassag} pixel"
        tk.Label(elonezet_ablak, text=info_szoveg, fg="white", bg="#252526", font=("Arial", 11)).pack(side=tk.BOTTOM,
                                                                                                      pady=5)

        max_meret = 220
        skalazas = max(1, int(max(szelesseg / max_meret, magassag / max_meret)))
        elonezet_kep = eredeti_kep.subsample(skalazas, skalazas) if skalazas > 1 else eredeti_kep

        lbl_kep = tk.Label(elonezet_ablak, image=elonezet_kep, bg="#1e1e1e", relief="solid", bd=1)
        lbl_kep.image = elonezet_kep
        lbl_kep.pack(side=tk.TOP, expand=True, padx=10, pady=10)

    except Exception as e:
        messagebox.showerror("Hiba",
                             f"Nem sikerült megnyitni a képet:\n{e}\n\n(Tipp: Használj PNG vagy GIF formátumot!)")


# --- Fájlkezelők ---
def fajl_megnyitasa():
    f = filedialog.askopenfilename(filetypes=[("MagyarKód", "*.mkod"), ("Minden fájl", "*.*")])
    if f:
        kod_szerkeszto.delete("1.0", tk.END)
        kod_szerkeszto.insert(tk.END, open(f, "r", encoding="utf-8").read())
        szintaxis_kiemeles()
        ablak.title(f"MagyarKód Szerkesztő - {f}")


def fajl_mentese():
    f = filedialog.asksaveasfilename(defaultextension=".mkod",
                                     filetypes=[("MagyarKód", "*.mkod"), ("Minden fájl", "*.*")])
    if f:
        open(f, "w", encoding="utf-8").write(kod_szerkeszto.get("1.0", tk.END).rstrip())
        ablak.title(f"MagyarKód Szerkesztő - {f}")


# --- Szintaxis Kiemelés ---
def szintaxis_kiemeles(event=None):
    szoveg = kod_szerkeszto.get("1.0", tk.END)
    for cimke in ["parancs", "vezerlo", "logika", "beepitett"]:
        kod_szerkeszto.tag_remove(cimke, "1.0", tk.END)

    szavak = {
        "parancs": [r'\bírd\b', r'\bkérd\b', r'\bfeladat\b', r'\bvissza\b'],
        "vezerlo": [r'\bha\b', r'\bkülönben\b', r'\bkülönben_ha\b', r'\bamíg\b', r'\bminden\b', r'\bbenne\b'],
        "logika": [r'\bés\b', r'\bvagy\b', r'\bnem\b', r'\bIgaz\b', r'\bHamis\b', r'\bSemmi\b'],
        "beepitett": [r'\bvéletlen\b', r'\bvárj\b', r'\bhossz\b', r'\begész\b', r'\bszöveg\b',
                      r'\bablak_méret\b', r'\bháttérszín\b', r'\btéglalap\b', r'\bkép_frissítés\b',
                      r'\blenyomva\b', r'\bkilépés_kérve\b', r'\bjáték_vége\b', r'\bkép_betöltés\b',
                      r'\bkép_rajzolás\b']
    }

    sorok = szoveg.split('\n')
    for i, sor in enumerate(sorok):
        for cimke, minta_lista in szavak.items():
            for minta in minta_lista:
                for t in re.finditer(minta, sor):
                    kod_szerkeszto.tag_add(cimke, f"{i + 1}.{t.start()}", f"{i + 1}.{t.end()}")


# --- Futtatás ---
def futtasd_a_kodot():
    if not pygame: return messagebox.showerror("Hiba", "A pygame modul hiányzik! Futtasd: pip install pygame")

    szotar = {
        "írd": "print", "kérd": "input", "ha ": "if ", "különben:": "else:",
        "különben_ha ": "elif ", "amíg ": "while ", "minden ": "for ", " benne ": " in ",
        "feladat ": "def ", "vissza ": "return ", " és ": " and ", " vagy ": " or ",
        " nem ": " not ", "Igaz": "True", "Hamis": "False", "Semmi": "None"
    }
    angol_kod = kod_szerkeszto.get("1.0", tk.END)
    for magy, ang in szotar.items(): angol_kod = angol_kod.replace(magy, ang)

    kimenet_tarolo = io.StringIO()
    sajat_fuggvenyek = {
        "input": lambda p="": simpledialog.askstring("Bemenet", p),
        "véletlen": random.randint, "várj": time.sleep, "hossz": len, "egész": int, "szöveg": str,
        "ablak_méret": mk_ablak_meret, "háttérszín": mk_hatterszin, "téglalap": mk_teglalap,
        "kép_frissítés": mk_kep_frissites, "lenyomva": mk_lenyomva, "kilépés_kérve": mk_kilepes_kerve,
        "játék_vége": mk_jatek_vege, "kép_betöltés": mk_kep_betoltes, "kép_rajzolás": mk_kep_rajzolás
    }

    try:
        with contextlib.redirect_stdout(kimenet_tarolo):
            exec(angol_kod, sajat_fuggvenyek)
    except Exception as e:
        mk_jatek_vege();
        print(f"Hiba a kódban:\n{e}")

    eredmeny_doboz.config(state=tk.NORMAL);
    eredmeny_doboz.delete("1.0", tk.END)
    eredmeny_doboz.insert(tk.END, kimenet_tarolo.getvalue());
    eredmeny_doboz.config(state=tk.DISABLED)


# --- GUI Felépítés ---
ablak = tk.Tk()
ablak.title("MagyarKód Szerkesztő - Névtelen.mkod")
ablak.geometry("850x720")
ablak.config(bg="#1e1e1e")

# Menüsor
menu_sor = tk.Menu(ablak)
ablak.config(menu=menu_sor)

fajl_menu = tk.Menu(menu_sor, tearoff=0)
menu_sor.add_cascade(label="Fájl", menu=fajl_menu)
fajl_menu.add_command(label="Megnyitás...", command=fajl_megnyitasa)
fajl_menu.add_command(label="Mentés másként...", command=fajl_mentese)
fajl_menu.add_separator()
fajl_menu.add_command(label="Kilépés", command=ablak.quit)

eszkozo_menu = tk.Menu(menu_sor, tearoff=0)
menu_sor.add_cascade(label="Eszközök", menu=eszkozo_menu)
eszkozo_menu.add_command(label="🖼️ Kép megnyitása / előnézet...", command=kep_megnyitasa_es_elonezet)

# Felső gombok
gomb_sav = tk.Frame(ablak, bg="#1e1e1e")
gomb_sav.pack(fill=tk.X, padx=10, pady=5)

futtatas_gomb = tk.Button(gomb_sav, text="▶ Kód Futtatása", bg="#E51400", fg="white", font=("Arial", 12, "bold"),
                          command=futtasd_a_kodot)
futtatas_gomb.pack(side=tk.LEFT, padx=5)

kep_gomb = tk.Button(gomb_sav, text="🖼️ Kép megnyitása / beszúrása", bg="#007ACC", fg="white", font=("Arial", 12),
                     command=kep_megnyitasa_es_elonezet)
kep_gomb.pack(side=tk.LEFT, padx=5)

kod_szerkeszto = tk.Text(ablak, height=18, font=("Consolas", 14), bg="#252526", fg="#d4d4d4", insertbackground="white")
kod_szerkeszto.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

kod_szerkeszto.tag_config("parancs", foreground="#569CD6", font=("Consolas", 14, "bold"))
kod_szerkeszto.tag_config("vezerlo", foreground="#C586C0", font=("Consolas", 14, "bold"))
kod_szerkeszto.tag_config("logika", foreground="#CE9178", font=("Consolas", 14, "bold"))
kod_szerkeszto.tag_config("beepitett", foreground="#FFD700", font=("Consolas", 14, "bold"))

kod_szerkeszto.bind("<KeyRelease>", szintaxis_kiemeles)

# Kezdő kód
jatek_kod = """# Kattints a fenti "🖼️ Kép megnyitása" gombra egy kép beszúrásához!
ablak_méret(800, 600)

amíg nem kilépés_kérve():
    háttérszín(20, 20, 40)
    kép_frissítés(60)

játék_vége()
"""
kod_szerkeszto.insert(tk.END, jatek_kod)
szintaxis_kiemeles()

tk.Label(ablak, text="Eredmény (Konzol):", fg="white", bg="#1e1e1e", font=("Arial", 11)).pack(pady=2)
eredmeny_doboz = tk.Text(ablak, height=6, font=("Consolas", 12), bg="#000000", fg="#4AF626")
eredmeny_doboz.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
eredmeny_doboz.config(state=tk.DISABLED)

ablak.mainloop()