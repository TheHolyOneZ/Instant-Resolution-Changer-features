import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from PIL import Image, ImageTk, ImageSequence
import requests
from io import BytesIO
import win32api
import win32con
import shutil
import winshell
import time
import platform
import psutil
import subprocess

# Ursprüngliche Einstellungen
original_resolution = "2560 x 1440"
original_refresh_rate = "165"

# URL des Galaxy-GIFs
url = "https://i.gifer.com/fxTQ.gif"

def get_hwid(command):
    try:
        result = subprocess.check_output(command, shell=True).decode().strip().split("\n")
        return result[-1] if result else "N/A"
    except Exception:
        return "N/A"

def show_system_info():
    bios_hwid = get_hwid("wmic bios get serialnumber")
    cpu_hwid = get_hwid("wmic cpu get processorid")
    mainboard_hwid = get_hwid("wmic baseboard get serialnumber")
    
    info = (
        f"Betriebssystem: {platform.system()} {platform.release()}\n"
        f"Prozessor: {platform.processor()}\n"
        f"Arbeitsspeicher: {psutil.virtual_memory().total // (1024 ** 3)} GB\n"
        f"Festplattenspeicher: {psutil.disk_usage('/').total // (1024 ** 3)} GB\n"
        f"BIOS HWID: {bios_hwid}\n"
        f"CPU HWID: {cpu_hwid}\n"
        f"Mainboard HWID: {mainboard_hwid}"
    )
    
    show_system_info_gui(info)

def show_system_info_gui(info):
    info_app = tk.Toplevel()
    info_app.title("Systeminformationen")
    info_app.geometry(f"{gif_width}x{gif_height}")

    info_background_label = tk.Label(info_app)
    info_background_label.place(relwidth=1, relheight=1)

    info_title_label = tk.Label(info_app, text="Systeminformationen", font=("Helvetica", 24, "bold"), bg="black", fg="red")
    info_title_label.place(relx=0.5, y=30, anchor=tk.CENTER)

    info_label = tk.Label(info_app, text=info, font=("Helvetica", 12), bg="black", fg="white", justify=tk.LEFT)
    info_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    stop_animation = threading.Event()

    def animate_info_gif():
        counter = 0
        while not stop_animation.is_set():
            try:
                img_frame = ImageTk.PhotoImage(gif_frames[counter])
                info_background_label.config(image=img_frame)
                info_background_label.image = img_frame
                counter = (counter + 1) % len(gif_frames)
                time.sleep(1 / 120)
            except tk.TclError:
                break

    thread = threading.Thread(target=animate_info_gif, daemon=True)
    thread.start()

    def on_close():
        stop_animation.set()
        info_app.destroy()

    exit_button = ttk.Button(info_app, text="Exit", command=on_close)
    exit_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
  
def show_credits():
    credits_app = tk.Toplevel()
    credits_app.title("Credits")
    credits_app.geometry(f"{gif_width}x{gif_height}")

    credits_background_label = tk.Label(credits_app)
    credits_background_label.place(relwidth=1, relheight=1)

    credits_label = tk.Label(credits_app, text="TheZ, ZoRyIsReal", font=("Helvetica", 24, "bold"), bg="black", fg="red")
    credits_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    stop_animation = threading.Event()

    def animate_credits_gif():
        counter = 0
        while not stop_animation.is_set():
            try:
                img_frame = ImageTk.PhotoImage(gif_frames[counter])
                credits_background_label.config(image=img_frame)
                credits_background_label.image = img_frame
                counter = (counter + 1) % len(gif_frames)
                time.sleep(1 / 120)
            except tk.TclError:
                break

    thread = threading.Thread(target=animate_credits_gif, daemon=True)
    thread.start()

    def on_close():
        stop_animation.set()
        credits_app.destroy()

    exit_button = ttk.Button(credits_app, text="Exit", command=on_close)
    exit_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

def apply_settings():
    resolution = resolution_var.get().split('x')
    width = int(resolution[0].strip())
    height = int(resolution[1].strip())
    refresh_rate = int(refresh_rate_var.get())

    devmode = win32api.EnumDisplaySettings(None, 0)
    devmode.PelsWidth = width
    devmode.PelsHeight = height
    devmode.DisplayFrequency = refresh_rate
    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT | win32con.DM_DISPLAYFREQUENCY

    result = win32api.ChangeDisplaySettings(devmode, win32con.CDS_TEST)
    if result == win32con.DISP_CHANGE_SUCCESSFUL:
        win32api.ChangeDisplaySettings(devmode, 0)
        messagebox.showinfo("Einstellungen angewendet", f"Resolution: {width}x{height}, Refresh Rate: {refresh_rate} Hz")
        show_effect()
    else:
        messagebox.showerror("Fehler", "Änderung der Auflösung fehlgeschlagen")

def reset_settings():
    resolution_var.set(original_resolution)
    refresh_rate_var.set(original_refresh_rate)

def reduce_game_delay():
    messagebox.showinfo("Spieleinstellungen", "Spielverzögerung wurde reduziert!")
    show_effect()

def clear_temp_files():
    temp_directories = [os.getenv('TEMP'), os.path.join(os.getenv('SystemRoot'), 'Temp')]
    
    try:
        for temp_path in temp_directories:
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                    except PermissionError:
                        pass
                for dir in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, dir))
                    except PermissionError:
                        pass
        
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        
        messagebox.showinfo("Temp Cleaner", "Temporäre Dateien wurden erfolgreich gelöscht und der Papierkorb wurde geleert!")
    except Exception as e:
        messagebox.showerror("Fehler bei Temp Cleaner", str(e))

def delete_old_files():
    folder_path = filedialog.askdirectory()
    if folder_path:
        now = time.time()
        cutoff = now - 30 * 86400

        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.stat(file_path).st_mtime < cutoff:
                        os.remove(file_path)
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    if os.stat(dir_path).st_mtime < cutoff:
                        shutil.rmtree(dir_path)
            messagebox.showinfo("Datei Reiniger", f"Dateien älter als 30 Tage im Ordner {folder_path} wurden gelöscht!")
        except Exception as e:
            messagebox.showerror("Fehler bei Datei Reiniger", str(e))

def on_enter(e):
    e.widget['background'] = '#e0e0e0'

def on_leave(e):
    e.widget['background'] = 'SystemButtonFace'

def animate_gif():
    counter = 0
    while True:
        img_frame = ImageTk.PhotoImage(gif_frames[counter])
        try:
            background_label.config(image=img_frame)
            background_label.image = img_frame
        except tk.TclError:
            break
        counter = (counter + 1) % len(gif_frames)
        time.sleep(1 / 120)

def show_effect():
    effect_label = tk.Label(app, text="Einstellung angewendet!", font=("Helvetica", 24), bg="yellow")
    effect_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    app.after(2000, effect_label.destroy)

def add_resolution():
    new_resolution = simpledialog.askstring("Neue Auflösung hinzufügen", "Gib die Auflösung im Format 'Breite x Höhe' ein (z.B. 1920 x 1080):")
    if new_resolution:
        try:
            width, height = map(int, new_resolution.lower().replace('x', ' ').split())
            formatted_resolution = f"{width} x {height}"
            if formatted_resolution not in resolutions:
                resolutions.append(formatted_resolution)
                resolutions.sort(key=lambda res: [int(i) for i in res.split(' x ')])
                resolution_menu['values'] = resolutions
            else:
                messagebox.showwarning("Warnung", "Diese Auflösung ist bereits in der Liste.")
        except ValueError:
            messagebox.showerror("Fehler", "Ungültiges Auflösungsformat. Bitte verwenden Sie das Format 'Breite x Höhe'.")

def remove_resolution():
    current_resolution = resolution_var.get()
    if (current_resolution in resolutions):
        resolutions.remove(current_resolution)
        resolution_menu['values'] = resolutions
        if resolutions:
            resolution_var.set(resolutions[0])
        else:
            resolution_var.set("")

def create_backup():
    source_dir = filedialog.askdirectory(title="Verzeichnis für Backup auswählen")
    if source_dir:
        backup_dir = filedialog.askdirectory(title="Backup-Speicherort auswählen")
        if backup_dir:
            try:
                shutil.copytree(source_dir, os.path.join(backup_dir, os.path.basename(source_dir) + "_backup"))
                messagebox.showinfo("Backup", "Backup erfolgreich erstellt!")
            except Exception as e:
                messagebox.showerror("Fehler bei Backup", str(e))

def restore_backup():
    backup_dir = filedialog.askdirectory(title="Backup-Verzeichnis auswählen")
    if backup_dir:
        restore_dir = filedialog.askdirectory(title="Zielverzeichnis für Wiederherstellung auswählen")
        if restore_dir:
            try:
                for item in os.listdir(backup_dir):
                    s = os.path.join(backup_dir, item)
                    d = os.path.join(restore_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
                messagebox.showinfo("Wiederherstellung", "Backup erfolgreich wiederhergestellt!")
            except Exception as e:
                messagebox.showerror("Fehler bei Wiederherstellung", str(e))

response = requests.get(url)
gif = Image.open(BytesIO(response.content))

gif_frames = [frame.copy().resize((frame.width * 2, frame.height * 2), Image.Resampling.LANCZOS) for frame in ImageSequence.Iterator(gif)]

gif_width, gif_height = gif_frames[0].size

app = tk.Tk()
app.title("Bildschirm Einstellungen")
app.geometry(f"{gif_width}x{gif_height}")

background_label = tk.Label(app)
background_label.place(relwidth=1, relheight=1)

title_label = tk.Label(app, text="TheZ's Res changer", font=("Helvetica", 24, "bold"), bg="black", fg="red")
title_label.place(relx=0.5, y=30, anchor=tk.CENTER)

style = ttk.Style()
style.configure("TFrame", background="black")
style.configure("TLabel", background="black", foreground="white", font=("Helvetica", 12))
style.configure("TCombobox", font=("Helvetica", 12))
style.configure("TButton", font=("Helvetica", 12, "bold"), background="gray", foreground="black")
style.map("TButton", background=[("active", "#e0e0e0")])

frame = ttk.Frame(app, padding="10", relief="sunken")
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

ttk.Label(frame, text="Resolution:").grid(row=0, column=0, sticky=tk.W)
resolutions = ["1280 x 720", "1828 x 1332", "1920 x 1080", "2048 x 872", "2560 x 1440", "3840 x 2160"]
resolution_var = tk.StringVar(value=original_resolution)
resolution_menu = ttk.Combobox(frame, textvariable=resolution_var, values=resolutions)
resolution_menu.grid(row=0, column=1, sticky=(tk.W, tk.E))
resolution_menu.current(resolutions.index(original_resolution))

ttk.Label(frame, text="Refresh Rate (Hz):").grid(row=1, column=0, sticky=tk.W)
refresh_rates = ["60", "120", "144", "165"]
refresh_rate_var = tk.StringVar(value=original_refresh_rate)
refresh_rate_menu = ttk.Combobox(frame, textvariable=refresh_rate_var, values=refresh_rates)
refresh_rate_menu.grid(row=1, column=1, sticky=(tk.W, tk.E))
refresh_rate_menu.current(refresh_rates.index(original_refresh_rate))

apply_button = ttk.Button(frame, text="Apply", command=apply_settings)
apply_button.grid(row=2, column=0, columnspan=2, pady="10")

reset_button = ttk.Button(frame, text="Reset", command=reset_settings)
reset_button.grid(row=3, column=0, columnspan=2, pady="10")

reduce_delay_button = ttk.Button(frame, text="Reduce Game Delay", command=reduce_game_delay)
reduce_delay_button.grid(row=4, column=0, columnspan=2, pady="10")

clear_temp_button = ttk.Button(frame, text="Clear Temp Files", command=clear_temp_files)
clear_temp_button.grid(row=5, column=0, columnspan=2, pady="10")

delete_old_files_button = ttk.Button(frame, text="Delete Old Files", command=delete_old_files)
delete_old_files_button.grid(row=6, column=0, columnspan=2, pady="10")

add_resolution_button = ttk.Button(frame, text="Add Resolution", command=add_resolution)
add_resolution_button.grid(row=7, column=0, pady="10")

remove_resolution_button = ttk.Button(frame, text="Remove Resolution", command=remove_resolution)
remove_resolution_button.grid(row=7, column=1, pady="10")

system_info_button = ttk.Button(frame, text="System Info", command=show_system_info)
system_info_button.grid(row=8, column=0, columnspan=2, pady="10")

create_backup_button = ttk.Button(frame, text="Create Backup", command=create_backup)
create_backup_button.grid(row=9, column=0, columnspan=2, pady="10")

restore_backup_button = ttk.Button(frame, text="Restore Backup", command=restore_backup)
restore_backup_button.grid(row=10, column=0, columnspan=2, pady="10")

credits_button = ttk.Button(frame, text="Credits", command=show_credits)
credits_button.grid(row=11, column=0, columnspan=2, pady="10")

exit_button = ttk.Button(frame, text="Exit", command=app.quit)
exit_button.grid(row=12, column=0, columnspan=2, pady="10")

apply_button.bind("<Enter>", on_enter)
apply_button.bind("<Leave>", on_leave)
reset_button.bind("<Enter>", on_enter)
reset_button.bind("<Leave>", on_leave)
reduce_delay_button.bind("<Enter>", on_enter)
reduce_delay_button.bind("<Leave>", on_leave)
clear_temp_button.bind("<Enter>", on_enter)
clear_temp_button.bind("<Leave>", on_leave)
delete_old_files_button.bind("<Enter>", on_enter)
delete_old_files_button.bind("<Leave>", on_leave)
add_resolution_button.bind("<Enter>", on_enter)
add_resolution_button.bind("<Leave>", on_leave)
remove_resolution_button.bind("<Enter>", on_enter)
remove_resolution_button.bind("<Leave>", on_leave)
system_info_button.bind("<Enter>", on_enter)
system_info_button.bind("<Leave>", on_leave)
create_backup_button.bind("<Enter>", on_enter)
create_backup_button.bind("<Leave>", on_leave)
restore_backup_button.bind("<Enter>", on_enter)
restore_backup_button.bind("<Leave>", on_leave)
credits_button.bind("<Enter>", on_enter)
credits_button.bind("<Leave>", on_leave)
exit_button.bind("<Enter>", on_enter)
exit_button.bind("<Leave>", on_leave)

frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=2)

threading.Thread(target=animate_gif, daemon=True).start()
app.mainloop()
