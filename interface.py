import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from fpdf import FPDF
import json 
import random
from csp import apply_backtracking
from apprNonSup import recommend_based_on_embeddings
global root
font_path_regular= "font/LiberationMono-Regular.ttf"
font_path_bold= "font/LiberationMono-Bold.ttf"

# Funzione per salvare le preferenze in un file JSON
def save_preferences(preferences):
    with open("user_preferences.json", "w") as file:
        json.dump(preferences, file)
    messagebox.showinfo("Preferences Saved", "Your preferences have been saved successfully")

# Funzione che genera un PDF con i suggerimenti per l'utente in base alle sue preferenze
def generate_pdf(recommendations, additional_recommendations, preferred_day, start_time, end_time):
    pdf = FPDF()
    pdf.add_page()
    
    # Imposta il font ed il titolo
    pdf.add_font('liberation_mono_regular', '', font_path_regular, uni=True)
    pdf.add_font('liberation_mono_bold', '', font_path_bold, uni=True)
    pdf.set_font("liberation_mono_bold", size=16)
    pdf.set_text_color(255, 0, 0)
    pdf.cell(0, 10, txt="Netflix Recommendations and Weekly Schedule", ln=True, align='C')
    pdf.ln(10)

    # Scrive lo schedule  ed i dettagli
    pdf.set_font("liberation_mono_regular", size=14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt=f"Your preferred schedule is:", ln=True)
    pdf.ln(5)
    
    pdf.set_font("liberation_mono_regular", size=12)
    pdf.cell(0, 10, txt=f"Day: {preferred_day}", ln=True)
    pdf.cell(0, 10, txt=f"Time: {start_time} - {end_time}", ln=True)
    pdf.ln(10)
    
    # Aggiungi una linea separatrice nera
    pdf.set_draw_color(0, 0, 0) 
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) 
    pdf.ln(5)

    # Intestazione dei primi 5 suggerimenti
    pdf.set_font("liberation_mono_bold", size=14)
    pdf.set_text_color(255, 0, 0)
    pdf.cell(0, 10, txt="Your 5 Recommendations:", ln=True)
    pdf.ln(5)
    
    # Scrive i 5 suggerimenti con una lista numerata e formattati
    pdf.set_font("liberation_mono_regular", size=12)
    pdf.set_text_color(0, 0, 0)
    for idx, result in enumerate(recommendations, 1):
        result_cleaned =  extract_title_duration_genres_extended(result)
        pdf.multi_cell(0, 10, f"{idx}. {result_cleaned}", border=0)
        pdf.ln(2)  # Spaziatura tra ogni suggerimento
    
    # Separatore per la sezione successiva
    pdf.ln(10)
    pdf.set_font("liberation_mono_bold", size=14)
    pdf.cell(0, 10, txt="You Might Also Like...", ln=True, align='C')
    pdf.ln(5)

    # Scrive i 3 suggerimenti aggiuntivi con una lista numerata e formattata
    pdf.set_font("liberation_mono_regular", size=12)
    for idx, result in enumerate(additional_recommendations, 1):
        result_cleaned = extract_title_duration_genres_extended(result)
        pdf.multi_cell(0, 10, f"{idx}. {result_cleaned}", border=0)
        pdf.ln(2)

    # Salva il PDF
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
        max_duration_var.set(210)
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
        
    # Debug: gestisce il caso in cui non ci siano generi disponibili per il tipo di contenuto selezionato
    if not genre_list:
        messagebox.showerror("Error", "No genre available for the selected content type.")

# Funzione che aggiorna dinamicamente il menù a discesa, che gestisce la selezione corrente
def update_day_selection(day_var, days_list):
    selected_day = day_var.get()
    
    # Pulisce le opzioni presenti
    day_dropdown['menu'].delete(0, 'end')
    
    # Aggiunge le nuove opzioni
    for day in days_list:
        day_dropdown['menu'].add_command(label=day, command=tk._setit(day_var, day))

    # Seleziona il valore di default
    if selected_day in days_list:
        day_var.set(selected_day)
    else:
        day_var.set(days_list[0])

# Funzione che estrae e formatta le info su film o serie TV.
# Le info che vengono estratte sono: titolo, durata e genere
def extract_title_duration_genres(recommendation):
    
    # Gestisce il caso in cui recommendation sia un dizionario
    if isinstance(recommendation, dict):
        title = recommendation.get('Title', 'Unknown Title')
        
        if recommendation.get('Is_movie'):
            duration = recommendation.get('Film_Duration', 'N/A')
            genres = ', '.join(recommendation.get('Genre_Film', []))
            return f"Title: {title}  Duration: {duration}\nGenres: {genres}"

        elif recommendation.get('Is_TVshow'):
            duration = recommendation.get('Show_Duration', 'N/A')
            genres = ', '.join(recommendation.get('Genre_Show', []))
            return f"Title: {title}  Number of Seasons: {duration}\nGenres: {genres}"
        
        else:
            return f"Title: {title}: Unknown Content"

    # Ritorna il contenuto originale se non corrisponde a nessun formato conosciuto
    return str(recommendation)

# Funzione che estrae e formatta le info dell'altra funzione, con l'aggiunta di descrizione e classificazione
def extract_title_duration_genres_extended(recommendation):
    # Chiama la funzione principale per ottenere il titolo, durata e generi
    basic_info = extract_title_duration_genres(recommendation)
    
    if isinstance(recommendation, dict):
        description = recommendation.get('Description', 'No Description Available')
        classification = recommendation.get('Classification', 'No Classification')
        return f"{basic_info}\nDescription: {description}\nClassification: {classification}"
    
    return basic_info

# Funzione che estrae il titolo di un contenuto suggerito.
def extract_title_from_recommendation(recommendation):
    # Controlla se i suggerimenti sono dei dizionari validi e che sia presente il titolo
    if isinstance(recommendation, dict) and 'Title' in recommendation:
        return recommendation['Title']
    else:
        print(f"Error: The recommendation format is invalid: {recommendation}")
        return "Unknown Title"

# Funzione che rimuove i duplicati dai suggerimenti
def remove_duplicates(initial_recommendations, additional_recommendations):
    # Estrae i titoli dai suggerimenti iniziali
    initial_titles = [rec['Title'] for rec in initial_recommendations if isinstance(rec, dict) and 'Title' in rec]

    # Filtra i duplicati dai suggerimenti aggiuntivi in base al titolo
    filtered_additional = [
        rec for rec in additional_recommendations
        if isinstance(rec, dict) and 'Title' in rec and rec['Title'] not in initial_titles
    ]

    # Per assicurare che non ci siano duplicati nei suggerimenti aggiuntivi..
    seen_titles = set()
    unique_additional = []
    for rec in filtered_additional:
        title = rec['Title']
        if title not in seen_titles:
            unique_additional.append(rec)
            seen_titles.add(title)

    return unique_additional

# Funzione che gestisce le preferenze dell'utente e richiama tutte le altre funzioni utili a tale scopo.
def submit_preferences(df, content_type_var, min_duration_var, max_duration_var, genre_var, day_var, start_time_var, end_time_var, root):
    content_type = content_type_var.get()
    Is_movie = content_type == "Movie"
    Is_TVshow = content_type == "TV Show"
    
    # Prende i valori di durata
    min_duration = min_duration_var.get()
    max_duration = max_duration_var.get()
    
    # Prende il genere selezionato
    selected_genres = [genre_var.get(i) for i in genre_var.curselection()]

    # Verifica se è stata effettuata una selezione dei generi valida
    if not selected_genres:
        messagebox.showerror("Error", "Please, select at least one genre.")
        return
    
    # Prende i giorni preferiti e l'orario
    preferred_day = day_var.get()
    start_time = start_time_var.get()
    end_time = end_time_var.get()

    # Salva le preferenze
    preferences = {
        "content_type": content_type,
        "min_duration": min_duration,
        "max_duration": max_duration,
        "genres": selected_genres,
        "preferred_day": preferred_day,
        "start_time": start_time,
        "end_time": end_time
    }
    save_preferences(preferences)

    # Filtra i risultati in base al tipo di contenuto selezionato e alle preferenze
    results = apply_backtracking(df, Is_movie, Is_TVshow, min_duration, max_duration, selected_genres)

    if len(results) > 0:
        # Genera 5 suggerimenti casuali rispettando il tipo di contenuto
        random_recommendations = random.sample(results, min(5, len(results)))

        # Seleziona automaticamente un suggerimento tra i 5 dati come output
        selected_item = random.choice(random_recommendations)
        selected_title = extract_title_from_recommendation(selected_item)

        # Genera 3 suggerimenti aggiuntivi rispettando il tipo di contenuto
        additional_recommendations = recommend_based_on_embeddings(df, selected_title, num_recommendations=3, content_type=content_type)
        
        # Rimuove i duplicati dai suggerimenti aggiuntivi
        filtered_additional_recommendations = remove_duplicates(random_recommendations, additional_recommendations)

        # Se non ci sono altri suggerimenti aggiuntivi, crea un backup dei suggerimenti
        if len(filtered_additional_recommendations) == 0:
            random_title = df[df['Is_TVshow' if Is_TVshow else 'Is_movie'] == 1]['Title'].sample(1).values[0]
            backup_recommendations = recommend_based_on_embeddings(df, random_title, num_recommendations=3, content_type=content_type)
            
            # Assicura che il backup dei suggerimenti non abbia duplicati
            filtered_additional_recommendations = remove_duplicates(random_recommendations, backup_recommendations)

        # Se i suggerimenti di backup sono ancora vuoti, mostra il messaggio
        if len(filtered_additional_recommendations) == 0:
            filtered_additional_recommendations = ["No additional recommendations available"]

        # Mostra i suggerimenti e genera il pdf
        display_schedule(preferred_day, start_time, end_time, random_recommendations, root, filtered_additional_recommendations)
        generate_pdf(random_recommendations, filtered_additional_recommendations[:3], preferred_day, start_time, end_time)
    else:
        messagebox.showinfo("No Results", "No results match your preferences.")

# Funzione per resettare i campi
def reset_fields(content_type_var, min_duration_var, max_duration_var, genre_var, day_var, start_time_var, end_time_var):
    content_type_var.set("Movie")
    min_duration_var.set(0)
    max_duration_var.set(210)
    genre_var.selection_clear(0, tk.END)
        
    # Reset dei campi relativi al giorno e all'orario
    day_var.set("Monday")
    start_time_var.set("00:00")
    end_time_var.set("00:00")

# Mostra la weekly schedule
def display_schedule(day, start_time, end_time, recommendations, root, additional_recommendations=None):
    # Crea una nuova finestra per il calendario
    calendar_window = tk.Toplevel(root)
    calendar_window.title("Weekly Schedule")
    calendar_window.configure(bg="#f7f7f7")
    calendar_window.resizable(False, False)  # Impedisce il ridimensionamento sia orizzontale che verticale
    
    # Giorni della settimana
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Configura il layout della griglia per espandersi
    for i, day_name in enumerate(days_of_week):
        # Imposta un peso maggiore per il giorno selezionato
        if day_name == day:
            calendar_window.columnconfigure(i, weight=70, minsize=200)  # Colonna selezionata più ampia
        else:
            calendar_window.columnconfigure(i, weight=1, minsize=100)
    
    # Header dei giorni della settimana
    header_frame = tk.Frame(calendar_window, bg="#333333")
    header_frame.grid(row=0, column=0, columnspan=7, sticky="ew")
    
    # Configura la larghezza delle colonne per permettere l'espansione
    for i in range(7):
        # Imposta un peso maggiore per la colonna del giorno selezionato
        header_frame.grid_columnconfigure(i, weight=50 if days_of_week[i] == day else 1)

    # Mostra la settimana ed il calendario
    for i, day_name in enumerate(days_of_week):
    
        # Crea e configura le label dei giorni della settimana
        label = tk.Label(
            header_frame,
            text=f"{day_name}\n{(datetime.now() - timedelta(days=datetime.now().weekday() - i)).strftime('%d %b %Y')}",
            font=("Arial", 10, "bold"),
            bg="#3b3b3b" if day_name != day else "#6a8fb6",  # Cambia colore se è il giorno selezionato
            fg="white",
            padx=10,
            pady=5,
            borderwidth=1,
            relief="ridge",
            wraplength=0,
            anchor="center"
        )
        label.grid(row=0, column=i, padx=2, pady=2, sticky="nsew")
        
    # Mostra lo slot di tempo preferito nel giorno selezionato
    time_label = tk.Label(
        calendar_window,
        text=f"{start_time} - {end_time}",
        bg="#d4edda",
        fg="#155724",
        font=("Arial", 10, "bold"),
        padx=5,
        pady=2,
        borderwidth=1,
        relief="groove"
    )
    time_label.grid(row=1, column=days_of_week.index(day), padx=5, pady=5, sticky="nsew")

    # Limita l'espansione dei suggerimenti con una larghezza massima 
    max_width = 400

    # Mostra i 5 suggerimenti iniziali
    initial_label = tk.Label(
        calendar_window,
        text="Initial 5 Recommendations",
        font=("Arial", 10, "bold"),
        fg="#333333",
        bg="#f7f7f7",
        pady=5
    )
    initial_label.grid(row=2, column=days_of_week.index(day), padx=2, pady=2, sticky="nsew")

    # Mostra il titolo, la durata, ed i generi per ogni suggerimento
    for i, rec in enumerate(recommendations):
        title_duration_genres = extract_title_duration_genres(rec)
        recommendation_frame = tk.Frame(
            calendar_window,
            bg="#d0e1f9",
            padx=5,
            pady=5,
            relief="solid",
            borderwidth=1,
            width= max_width
        )
        recommendation_frame.grid(row=i + 3, column=days_of_week.index(day), padx=2, pady=2, sticky="nsew")
        recommendation_label = tk.Label(
            recommendation_frame,
            text=title_duration_genres,
            bg="#d0e1f9",
            font=("Arial", 9),
            justify='center',
            wraplength=400
        )
        recommendation_label.pack(anchor='center', fill='x')  # Centra l'etichetta all'interno del frame

    # Crea una separazione tra i 5 suggerimenti ed i 3 aggiuntivi
    if additional_recommendations:
        separator = tk.Label(
            calendar_window,
            text="You might also like...",
            font=("Arial", 10, "bold"),
            fg="#333333",
            bg="#f7f7f7",
            pady=5
        )
        separator.grid(row=i + 4, column=days_of_week.index(day), padx=2, pady=5, sticky="nsew")

        for j, rec in enumerate(additional_recommendations):
            # Applica la funzione di formattazione
            title_duration_genres = extract_title_duration_genres(rec)
            additional_frame = tk.Frame(
                calendar_window,
                bg="#fff3cd",
                padx=5,
                pady=5,
                relief="solid",
                borderwidth=1,
                width= max_width
            )
            additional_frame.grid(row=i + j + 5, column=days_of_week.index(day), padx=2, pady=2, sticky="nsew")
            recommendation_label = tk.Label(
                additional_frame,
                text=title_duration_genres,
                bg="#fff3cd",
                font=("Arial", 9),
                justify='center',
                wraplength=400
            )

            recommendation_label.pack(anchor='w', fill='x')

    return calendar_window

# Funzione per il controllo del formato dell'ora inserito dall'utente
def validate_time_format(value):
    if value == "":
        return True  # Permetti di lasciare il campo vuoto (per reset)
    if len(value) != 5:
        return False
    if value[2] != ":":
        return False
    hours, minutes = value.split(":")
    if not (hours.isdigit() and minutes.isdigit()):
        return False
    if not (0 <= int(hours) < 24 and 0 <= int(minutes) < 60):
        return False
    return True

# Funzione per validare il formato
def on_validate(P):
    if P == "":
        return True  # Permetti i campi vuoti per il reset senza mostrare errori
    if validate_time_format(P):
        return True
    else:
        messagebox.showerror("Invalid Time", "Please enter a valid time in the format HH:MM (00:00 - 23:59).")
        return False

# Funzione che crea il frame del time
def create_time_frame(root):
    time_frame = tk.LabelFrame(root, text="Preferred Time Interval")
    time_frame.pack(fill="x", padx=5, pady=5)

    global start_time_var, end_time_var
    start_time_var= tk.StringVar(value="00:00")
    end_time_var = tk.StringVar(value="00:00")

    vcmd = (root.register(on_validate), '%P')

    tk.Label(time_frame, text="Start Time").pack(side="left", padx=5)
    tk.Entry(time_frame, textvariable=start_time_var, width=5, validate="focusout", validatecommand=vcmd).pack(side="left", padx=5)
    tk.Label(time_frame, text="End Time").pack(side="left", padx=5)
    tk.Entry(time_frame, textvariable=end_time_var, width=5, validate="focusout", validatecommand=vcmd).pack(side="left", padx=5)
   
# Funzione per creare e avviare l'interfaccia grafica
def create_interface(df):
    global day_dropdown
    root = tk.Tk()
    root.title("Netflix Recommendation System")
    root.resizable(False, False)  # Impedisce il ridimensionamento sia orizzontale che verticale
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
    max_duration_var = tk.IntVar(value=210)
    
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
    
    # Gestione menu a tendina per la settimana
    day_var = tk.StringVar(value="Monday")
    # Lista dei giorni disponibili
    days_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # Crea un menu a discesa per la selezione dei giorni
    day_dropdown = tk.OptionMenu(root, day_var, *days_list)
    day_dropdown.pack()
    # Chiama la funzione per aggiornare la selezione dei giorni
    update_day_selection(day_var, days_list)
    
    create_time_frame(root)

    # Frame per i pulsanti
    button_frame = tk.Frame(root)
    button_frame.pack(fill="x", padx=5, pady=5)

    ttk.Button(button_frame, text="Submit", command=lambda: submit_preferences(
        df, content_type_var, min_duration_var, max_duration_var, genre_var, day_var, start_time_var, end_time_var, root)).pack(side="right", padx=5)
    ttk.Button(button_frame, text="Reset", command=lambda: reset_fields(
        content_type_var, min_duration_var, max_duration_var, genre_var, day_var, start_time_var, end_time_var)).pack(side="left", padx=5)

    # Avvio dell'interfaccia grafica
    root.mainloop()

