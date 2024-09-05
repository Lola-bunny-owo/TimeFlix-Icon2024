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

def clean_text(text):
    # Codifica in 'ascii' ignorando i caratteri non supportati
    return text.encode('ascii', 'ignore').decode('ascii')

def generate_pdf(results, preferred_day, start_time, end_time):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Netflix Recommendations and Weekly Schedule", ln=True, align='C')
    pdf.ln(10)

    # Scrivi i risultati filtrati nel PDF
    pdf.cell(200, 10, txt="Here are your recommendations:", ln=True)
    pdf.ln(10)
    for result in results:
        result_cleaned = clean_text(result)
        pdf.multi_cell(0, 10, result_cleaned)
        pdf.ln(5)

    # Scrivi la pianificazione settimanale nel PDF
    pdf.cell(200, 10, txt=f"Your preferred schedule is:", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Day: {preferred_day}", ln=True)
    pdf.cell(200, 10, txt=f"Time: {start_time} - {end_time}", ln=True)

    # Salva il file PDF
    try:
        pdf.output("Netflix_Recommendations_and_Schedule.pdf")
        messagebox.showinfo("PDF Generated", "The PDF has been successfully generated with your schedule.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while generating the PDF: {e}")


# Funzione per aggiornare il frame della durata in base al tipo di contenuto selezionato
def update_duration_frame(content_type, duration_frame, min_duration_var, max_duration_var):
    # Rimuove tutti i widget esistenti nel frame della durata
    for widget in duration_frame.winfo_children():
        widget.destroy()

    # Aggiunge i widget in base al tipo di contenuto selezionato
    if content_type.get() == "Movie":
        duration_frame.config(text="Duration (Minutes)")
        tk.Label(duration_frame, text="Min Duration").pack(side="left", padx=5)
        tk.Entry(duration_frame, textvariable=min_duration_var, width=5).pack(side="left", padx=5)
        tk.Label(duration_frame, text="Max Duration").pack(side="left", padx=5)
        tk.Entry(duration_frame, textvariable=max_duration_var, width=5).pack(side="left", padx=5)
    else:  # TV Show
        duration_frame.config(text="Duration (Seasons)")
        tk.Label(duration_frame, text="Min Seasons").pack(side="left", padx=5)
        tk.Entry(duration_frame, textvariable=min_duration_var, width=5).pack(side="left", padx=5)
        tk.Label(duration_frame, text="Max Seasons").pack(side="left", padx=5)
        tk.Entry(duration_frame, textvariable=max_duration_var, width=5).pack(side="left", padx=5)
        
     # Imposta i valori predefiniti per min e max duration / seasons
    if content_type.get() == "Movie":
        min_duration_var.set(0)
        max_duration_var.set(200)
    else:  # TV Show
        min_duration_var.set(1)
        max_duration_var.set(10)

# Funzione per aggiornare la lista dei generi basata sul tipo di contenuto
def update_genre_list(content_type, genre_var, df):
    genre_list = []
    
    if content_type == "Movie" and 'Genre_Film' in df.columns:
        genre_list = sorted(set(genre for sublist in df['Genre_Film'].dropna() for genre in sublist))
    elif content_type == "TV Show" and 'Genre_Show' in df.columns:
        genre_list = sorted(set(genre for sublist in df['Genre_Show'].dropna() for genre in sublist))
    
    genre_var.delete(0, tk.END)
    for genre in genre_list:
        genre_var.insert(tk.END, genre)

# Funzione che filtra i contenuti in base alle preferenze dell'utente
def preferences_filter(df, is_movie, is_show, min_duration, max_duration, selected_genres):
    filtered_results = []

    # Maschera booleana per i generi basata sul tipo di contenuto
    if is_movie:
        genre_mask = df['Genre_Film'].apply(lambda x: any(genre in selected_genres for genre in x))
        duration_mask = (df['Film_Duration'].fillna(0) >= min_duration) & (df['Film_Duration'].fillna(0) <= max_duration)
        type_mask = df['Is_Movie'] == 1
    elif is_show:
        genre_mask = df['Genre_Show'].apply(lambda x: any(genre in selected_genres for genre in x))
        duration_mask = (df['Show_Duration'].fillna(0) >= min_duration) & (df['Show_Duration'].fillna(0) <= max_duration)
        type_mask = df['Is_TVShow'] == 1
    else:
        return []

    # Filtro finale
    filtered_df = df[genre_mask & duration_mask & type_mask] # Se qui si aggiunge un .head(5), ad esempio il filtro contiene solo 5 contenuti

    # Creazione della lista di risultati formattati
    for _, item in filtered_df.iterrows():
        if is_movie:
            filtered_results.append(f"Movie - {item['Title']} - Duration: {item.get('Film_Duration', 'N/A')} - Genres: {', '.join(item.get('Genre_Film', []))}")
        elif is_show:
            filtered_results.append(f"TV Show - {item['Title']} - Seasons: {item.get('Show_Duration', 'N/A')} - Genres: {', '.join(item.get('Genre_Show', []))}")

    return filtered_results

# Funzione per raccogliere le preferenze dell'utente
def submit_preferences(df, content_type_var, min_duration_var, max_duration_var, genre_var, day_var, start_time_var, end_time_var, root):
    
    content_type = content_type_var.get()
    is_movie = content_type == "Movie"
    is_show = content_type == "TV Show"
    
    # Ottieni i valori delle variabili di durata
    min_duration = min_duration_var.get()
    max_duration = max_duration_var.get()

    # Ottieni i generi selezionati
    selected_genres = [genre_var.get(i) for i in genre_var.curselection()]

    # Ottieni il giorno della settimana e l'intervallo di tempo
    preferred_day = day_var.get()
    start_time = start_time_var.get()
    end_time = end_time_var.get()

    preferences = {
        "content_type": content_type,
        "min_duration": min_duration,
        "max_duration": max_duration,
        "genres": selected_genres,
        "preferred_day": preferred_day,
        "start_time": start_time,
        "end_time": end_time
    }

    save_preferences(preferences)  # Salva le preferenze in un file
    
    # Passa i parametri al filtro
    results = preferences_filter(df, is_movie, is_show, min_duration, max_duration, selected_genres)
    
    if len(results) > 0:
        # Passa la lista di raccomandazioni (massimo 5) alla funzione display_schedule
        display_schedule(preferred_day, start_time, end_time, results[:5], root)
        generate_pdf(results, preferred_day, start_time, end_time)
    else:
        messagebox.showinfo("No Results", "No results match your preferences.")

# Funzione per visualizzare la pianificazione settimanale nel calendario
def display_schedule(day, start_time, end_time, recommendations, root):
    # Crea una finestra secondaria per il calendario
    calendar_window = tk.Toplevel(root)
    calendar_window.title("Weekly Schedule")

    # Giorni della settimana
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Crea una griglia di etichette per rappresentare il calendario
    for i, day_name in enumerate(days_of_week):
        label = tk.Label(calendar_window, text=day_name, font=("Arial", 10, "bold"))
        label.grid(row=0, column=i, padx=5, pady=5)

    # Imposta il giorno e l'orario pianificato
    time_label = tk.Label(calendar_window, text=f"{start_time} - {end_time}", bg="white", font=("Arial", 10))
    col_index = days_of_week.index(day)  # Trova l'indice del giorno selezionato
    time_label.grid(row=1, column=col_index, padx=5, pady=5)

    # Mostra le raccomandazioni nel giorno selezionato (fino a 5)
    for i, rec in enumerate(recommendations[:5]):  # Mostra solo le prime 5 raccomandazioni
        recommendation_label = tk.Label(calendar_window, text=rec, bg="white", font=("Arial", 8))
        recommendation_label.grid(row=i + 2, column=col_index, padx=5, pady=5)


# Funzione per resettare i campi
def reset_fields(content_type_var, min_duration_var, max_duration_var, genre_var):
    content_type_var.set("Movie")
    min_duration_var.set(0)
    max_duration_var.set(200)
    genre_var.selection_clear(0, tk.END)


# Funzione per creare e avviare l'interfaccia grafica
def create_interface(df):
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
    
    # Variabili per la durata
    min_duration_var = tk.IntVar(value=0)
    max_duration_var = tk.IntVar(value=200)
    
    tk.Label(duration_frame, text="Min Duration").pack(side="left", padx=5)
    tk.Entry(duration_frame, textvariable=min_duration_var, width=5).pack(side="left", padx=5)
    tk.Label(duration_frame, text="Max Duration").pack(side="left", padx=5)
    tk.Entry(duration_frame, textvariable=max_duration_var, width=5).pack(side="left", padx=5)

    # Aggiorna il frame della durata quando cambia il tipo di contenuto
    content_type_var.trace_add('write', lambda *args: update_duration_frame(
        content_type_var, duration_frame, min_duration_var, max_duration_var))

    # Frame per i generi
    genre_frame = tk.LabelFrame(root, text="Genres")
    genre_frame.pack(fill="x", padx=5, pady=5)

    genre_var = tk.Listbox(genre_frame, selectmode="multiple", height=6)
    genre_var.pack(fill="x", padx=5, pady=5)
    
    # Aggiorna la lista dei generi basata sul tipo di contenuto iniziale
    update_genre_list(content_type_var.get(), genre_var, df)

    # Aggiorna la lista dei generi quando cambia il tipo di contenuto
    content_type_var.trace_add('write', lambda *args: update_genre_list(content_type_var.get(), genre_var, df))

    # Frame per la selezione del giorno della settimana
    day_frame = tk.LabelFrame(root, text="Preferred Day of the Week")
    day_frame.pack(fill="x", padx=5, pady=5)

    # Aggiungi una lista di selezione per i giorni della settimana
    day_var = tk.StringVar(value="Monday")
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_menu = ttk.Combobox(day_frame, textvariable=day_var, values=days_of_week, state="readonly")
    day_menu.pack(padx=5, pady=5)
    day_menu.current(0)  # Seleziona "Monday" di default

    # Frame per la selezione dell'intervallo di tempo
    time_frame = tk.LabelFrame(root, text="Preferred Time Interval")
    time_frame.pack(fill="x", padx=5, pady=5)

    # Variabili per l'orario di inizio e fine
    start_time_var = tk.StringVar(value="00:00")
    end_time_var = tk.StringVar(value="00:00")

    tk.Label(time_frame, text="Start Time").pack(side="left", padx=5)
    tk.Entry(time_frame, textvariable=start_time_var, width=5).pack(side="left", padx=5)
    tk.Label(time_frame, text="End Time").pack(side="left", padx=5)
    tk.Entry(time_frame, textvariable=end_time_var, width=5).pack(side="left", padx=5)

    # Frame per i pulsanti
    button_frame = tk.Frame(root)
    button_frame.pack(fill="x", padx=5, pady=5)

    ttk.Button(button_frame, text="Submit", command=lambda: submit_preferences(
        df, content_type_var, min_duration_var, max_duration_var, genre_var, day_var, start_time_var, end_time_var, root)).pack(side="right", padx=5)
    ttk.Button(button_frame, text="Reset", command=lambda: reset_fields(
        content_type_var, min_duration_var, max_duration_var, genre_var, day_var, start_time_var, end_time_var)).pack(side="left", padx=5)

    # Avvio dell'interfaccia grafica
    root.mainloop()
    
    # Funzione per resettare i campi
def reset_fields(content_type_var, min_duration_var, max_duration_var, genre_var, day_var, start_time_var, end_time_var):
    content_type_var.set("Movie")
    min_duration_var.set(0)
    max_duration_var.set(200)
    genre_var.selection_clear(0, tk.END)
        
    # Reset dei campi relativi al giorno e all'orario
    day_var.set("Monday")
    start_time_var.set("00:00")
    end_time_var.set("00:00")
