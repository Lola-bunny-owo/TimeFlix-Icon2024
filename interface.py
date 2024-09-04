import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import datetime
from fpdf import FPDF
import json  # Importa il modulo JSON per salvare le preferenze

# Funzione per salvare le preferenze in un file JSON
def save_preferences(preferences):
    with open("user_preferences.json", "w") as file:
        json.dump(preferences, file)
    messagebox.showinfo("Preferences Saved", "Your preferences have been saved successfully")

# Funzione per visualizzare i risultati su un calendario
def generate_calendar(results, root):
    now = datetime.now()
    cal = calendar.TextCalendar(calendar.SUNDAY)
    cal_str = cal.formatmonth(now.year, now.month)

    top = tk.Toplevel(root)
    top.title("Calendar")
    
    cal_label = tk.Label(top, text=cal_str, font=("Courier", 10))
    cal_label.pack(pady=10)

    result_label = tk.Label(top, text="\n".join(results), justify='left')
    result_label.pack(pady=10)

def generate_pdf(results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Netflix Recommendations", ln=True, align='C')
    pdf.ln(10)
    
    for result in results:
        pdf.multi_cell(0, 10, result)
        pdf.ln(5)
    
    pdf.output("Netflix_Recommendations.pdf")
    messagebox.showinfo("PDF Generated", "The PDF has been successfully generated")

# Funzione per raccogliere le preferenze dell'utente
def submit_preferences(content_type_var, min_duration_var, max_duration_var, genre_var, cast_entry, root):
    content_type = content_type_var.get()
    min_duration = min_duration_var.get()
    max_duration = max_duration_var.get()
    genres = [genre_var.get(i) for i in genre_var.curselection()]
    cast = cast_entry.get()

    preferences = {
        "content_type": content_type,
        "min_duration": min_duration,
        "max_duration": max_duration,
        "genres": genres,
        "cast": cast
    }

    save_preferences(preferences)  # Salva le preferenze in un file

    # Qui andrebbe implementata la logica per filtrare il dataset in base alle preferenze.
    # Per ora, inseriamo dei dati di esempio.
    results = [
        f"{content_type} - Title 1 - 100 min - {', '.join(genres)} - Cast: {cast}",
        f"{content_type} - Title 2 - 120 min - {', '.join(genres)} - Cast: {cast}"
    ]
    
    if len(results) > 0:
        generate_pdf(results)
        generate_calendar(results, root)
    else:
        messagebox.showinfo("No Results", "No results match your preferences.")

# Funzione per resettare i campi
def reset_fields(content_type_var, min_duration_var, max_duration_var, genre_var, cast_entry):
    content_type_var.set("Movie")
    min_duration_var.set(0)
    max_duration_var.set(200)
    genre_var.selection_clear(0, tk.END)
    cast_entry.delete(0, tk.END)

# Funzione per creare e avviare l'interfaccia grafica
def create_interface():
    root = tk.Tk()
    root.title("Netflix Recommendation System")

    # Frame per il tipo di contenuto
    type_frame = tk.LabelFrame(root, text="Content Type")
    type_frame.pack(fill="x", padx=5, pady=5)

    content_type_var = tk.StringVar(value="Movie")
    ttk.Radiobutton(type_frame, text="Movie", variable=content_type_var, value="Movie").pack(side="left", padx=5)
    ttk.Radiobutton(type_frame, text="TV Show", variable=content_type_var, value="TV Show").pack(side="left", padx=5)

    # Frame per la durata
    duration_frame = tk.LabelFrame(root, text="Duration (Minutes)")
    duration_frame.pack(fill="x", padx=5, pady=5)

    min_duration_var = tk.IntVar(value=0)
    max_duration_var = tk.IntVar(value=200)
    tk.Label(duration_frame, text="Min Duration").pack(side="left", padx=5)
    tk.Entry(duration_frame, textvariable=min_duration_var, width=5).pack(side="left", padx=5)
    tk.Label(duration_frame, text="Max Duration").pack(side="left", padx=5)
    tk.Entry(duration_frame, textvariable=max_duration_var, width=5).pack(side="left", padx=5)

    # Frame per i generi
    genre_frame = tk.LabelFrame(root, text="Genres")
    genre_frame.pack(fill="x", padx=5, pady=5)

    genres_list = ["Action", "Comedy", "Drama", "Fantasy", "Horror", "Romance", "Sci-Fi", "Thriller"]
    genre_var = tk.Listbox(genre_frame, selectmode="multiple", height=6)
    for genre in genres_list:
        genre_var.insert(tk.END, genre)
    genre_var.pack(fill="x", padx=5, pady=5)

    # Frame per il cast
    cast_frame = tk.LabelFrame(root, text="Cast (Optional)")
    cast_frame.pack(fill="x", padx=5, pady=5)

    cast_entry = tk.Entry(cast_frame)
    cast_entry.pack(fill="x", padx=5, pady=5)

    # Frame per i pulsanti
    button_frame = tk.Frame(root)
    button_frame.pack(fill="x", padx=5, pady=5)

    ttk.Button(button_frame, text="Submit", command=lambda: submit_preferences(
        content_type_var, min_duration_var, max_duration_var, genre_var, cast_entry, root)).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Reset", command=lambda: reset_fields(
        content_type_var, min_duration_var, max_duration_var, genre_var, cast_entry)).pack(side="right", padx=5)

    # Avvio dell'interfaccia grafica
    root.mainloop()
