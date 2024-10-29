import os
import sqlite3
import pygame
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk  # For handling images

# Initialize Pygame mixer
pygame.mixer.init()

# Connect to SQLite database
conn = sqlite3.connect('mp3_player.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,  -- Ensure unique song titles
    file_path TEXT NOT NULL
)
''')

conn.commit()

# Tkinter GUI
root = Tk()
root.title("MP3 Player with Database")
root.geometry("600x500")

# Load background image from the 'images' folder
bg_image_path = os.path.join("images", "background.jpg")
bg_image = Image.open(bg_image_path)
bg_image = bg_image.resize((700, 500), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

current_song = None
paused = False

# Functions
def add_song_to_db(title, file_path):
    try:
        cursor.execute("INSERT INTO songs (title, file_path) VALUES (?, ?)", (title, file_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError:  # Handle duplicate title
        return False

def load_song():
    global current_song
    song_path = filedialog.askopenfilename(title="Select an MP3 file", filetypes=(("MP3 Files", "*.mp3"),))
    if song_path:
        title = os.path.basename(song_path)
        if add_song_to_db(title, song_path):
            songs_listbox.insert(END, title)
        else:
            messagebox.showwarning("Warning", f"Song '{title}' is already in the database.")

def play_song():
    global paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        selected_song = songs_listbox.get(ACTIVE)
        cursor.execute("SELECT file_path FROM songs WHERE title = ?", (selected_song,))
        song = cursor.fetchone()
        if song:
            pygame.mixer.music.load(song[0])
            pygame.mixer.music.play()

def pause_song():
    global paused
    pygame.mixer.music.pause()
    paused = True

def stop_song():
    pygame.mixer.music.stop()

# GUI Components
playlist_label = Label(root, text="Songs", font=("Helvetica", 20, 'bold'), bg="#d9d9d9", fg="black")
playlist_label.pack(pady=10)

# Set songs listbox with Alice Blue background
songs_listbox = Listbox(root, height=10, font=("Helvetica", 14), selectmode=SINGLE, bg="#f0f8ff")
songs_listbox.pack(pady=5)

# Color animation functions
def on_enter(e):
    e.widget['bg'] = '#8c8c8c'

def on_leave(e):
    e.widget['bg'] = '#d9d9d9'

def on_click(e):
    e.widget['bg'] = '#5c5c5c'

# Controls Frame
controls_frame = Frame(root, bg="#d9d9d9")
controls_frame.pack(pady=20)

# Animated color buttons
load_button = Button(controls_frame, text="Load Song", command=load_song, font=("Helvetica", 12), bg="#d9d9d9", bd=0)
play_button = Button(controls_frame, text="Play", command=play_song, font=("Helvetica", 12), bg="#d9d9d9", bd=0)
pause_button = Button(controls_frame, text="Pause", command=pause_song, font=("Helvetica", 12), bg="#d9d9d9", bd=0)
stop_button = Button(controls_frame, text="Stop", command=stop_song, font=("Helvetica", 12), bg="#d9d9d9", bd=0)

# Bind hover and click events for animations
for button in [load_button, play_button, pause_button, stop_button]:
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    button.bind("<ButtonPress>", on_click)

# Arrange buttons in a grid
load_button.grid(row=0, column=0, padx=5)
play_button.grid(row=0, column=1, padx=5)
pause_button.grid(row=0, column=2, padx=5)
stop_button.grid(row=0, column=3, padx=5)

# Load existing songs
cursor.execute("SELECT title FROM songs")
songs = cursor.fetchall()
for song in songs:
    songs_listbox.insert(END, song[0])

# Run the application
root.mainloop()

# Close the database connection on exit
conn.close()
