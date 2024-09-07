import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import datetime, timedelta
from fpdf import FPDF
import json  # Importa il modulo JSON per salvare le preferenze
import random
from apprNonSup import recommend_based_on_embeddings

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
    
# Codifica in 'ascii' ignorando i caratteri non supportati
def clean_text(text):
    return text.encode('ascii', 'ignore').decode('ascii')


def generate_pdf(recommendations, additional_recommendations, preferred_day, start_time, end_time):
    pdf = FPDF()
    pdf.add_page()
    
    # Set the font and title
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Netflix Recommendations and Weekly Schedule", ln=True, align='C')
    pdf.ln(10)

    # Write the schedule in the PDF
    pdf.cell(200, 10, txt=f"Your preferred schedule is:", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Day: {preferred_day}", ln=True)
    pdf.cell(200, 10, txt=f"Time: {start_time} - {end_time}", ln=True)
    pdf.ln(10)

    # Write the initial 5 recommendations
    pdf.cell(200, 10, txt="Initial 5 Recommendations:", ln=True)
    pdf.ln(5)
    for result in recommendations:
        result_cleaned = extract_title_duration_genres(result)
        pdf.multi_cell(0, 10, result_cleaned)
        pdf.ln(2)  # Spacing between each recommendation
    
    # Separator
    pdf.ln(5)
    pdf.cell(200, 10, txt="You might also like...", ln=True, align='C')
    pdf.ln(5)

    # Write the additional 3 recommendations
    for result in additional_recommendations:  # Fix: Show the additional 3 instead of repeating
        result_cleaned = extract_title_duration_genres(result)
        pdf.multi_cell(0, 10, result_cleaned)
        pdf.ln(2)

    # Save the PDF
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
        
def show_recommendations(df, selected_title):
    # Get the recommendations
    recommendations = recommend_based_on_embeddings(df, selected_title)

    # Display the recommendations in the UI
    recommendation_frame = tk.LabelFrame(root, text="Recommended Content")
    recommendation_frame.pack(fill="x", padx=5, pady=5)

    for rec in recommendations:
        tk.Label(recommendation_frame, text=rec).pack()

# Funzione che filtra i contenuti in base alle preferenze dell'utente
def preferences_filter(df, Is_movie, Is_TVshow, min_duration, max_duration, selected_genres):
    filtered_results = []

    # Maschera booleana per i generi basata sul tipo di contenuto
    if Is_movie:
        genre_mask = df['Genre_Film'].apply(lambda x: any(genre in selected_genres for genre in x))
        duration_mask = (df['Film_Duration'].fillna(0) >= min_duration) & (df['Film_Duration'].fillna(0) <= max_duration)
        type_mask = df['Is_movie'] == 1
    elif Is_TVshow:
        genre_mask = df['Genre_Show'].apply(lambda x: any(genre in selected_genres for genre in x))
        duration_mask = (df['Show_Duration'].fillna(0) >= min_duration) & (df['Show_Duration'].fillna(0) <= max_duration)
        type_mask = df['Is_TVshow'] == 1
    else:
        return []

    # Filtro finale
    filtered_df = df[genre_mask & duration_mask & type_mask] # Se qui si aggiunge un .head(5), ad esempio il filtro contiene solo 5 contenuti

    # Creazione della lista di risultati formattati
    for _, item in filtered_df.iterrows():
        if Is_movie:
            filtered_results.append(f"Movie - {item['Title']} - Duration: {item.get('Film_Duration', 'N/A')} - Genres: {', '.join(item.get('Genre_Film', []))}")
        elif Is_TVshow:
            filtered_results.append(f"TV Show - {item['Title']} - Seasons: {item.get('Show_Duration', 'N/A')} - Genres: {', '.join(item.get('Genre_Show', []))}")

    return filtered_results

def extract_title_duration_genres(recommendation):
    # The expected format is "Movie/TV Show - Title - Duration/Seasons - Genres"
    parts = recommendation.split(" - ")
    
    if len(parts) >= 4:
        title = parts[1].strip()
        duration_or_seasons = parts[2].strip()
        genres = parts[3].replace("Genres: ", "").strip()  # Clean up "Genres: " prefix
        return f"{title}: {duration_or_seasons}\nGenres: {genres}"
    return recommendation  # Fallback in case the format doesn't match


def extract_title_from_recommendation(recommendation):
    # The expected format is "Movie/TV Show - Title - Duration/Seasons - Genres"
    parts = recommendation.split(" - ")
    
    # We expect the second part to be the title
    if len(parts) > 1:
        return parts[1].strip()  # Return the title and remove any extra spaces
    return recommendation  # Fallback to the whole string if it doesn't match the format


def submit_preferences(df, content_type_var, min_duration_var, max_duration_var, genre_var, day_var, start_time_var, end_time_var, root):
    content_type = content_type_var.get()
    Is_movie = content_type == "Movie"
    Is_TVshow = content_type == "TV Show"
    
    # Get the duration values
    min_duration = min_duration_var.get()
    max_duration = max_duration_var.get()

    # Get the selected genres
    selected_genres = [genre_var.get(i) for i in genre_var.curselection()]

    # Get preferred day and time
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

    save_preferences(preferences)  # Save preferences to a file
    
    # Filter results based on user preferences
    results = preferences_filter(df, Is_movie, Is_TVshow, min_duration, max_duration, selected_genres)
    
    if len(results) > 0:
        # Generate 5 random recommendations
        random_recommendations = random.sample(results, min(5, len(results)))

        # Automatically select one recommendation from the 5 (randomly)
        selected_item = random.choice(random_recommendations)
        
        # Extract the actual title from the selected item
        selected_title = extract_title_from_recommendation(selected_item)
        
        # Generate 3 additional recommendations based on the selected title
        additional_recommendations = recommend_based_on_embeddings(df, selected_title)

        # Show the calendar with both the initial 5 and additional 3 recommendations
        display_schedule(preferred_day, start_time, end_time, random_recommendations, root, additional_recommendations)
        
        # Generate the PDF with the separation between the 5 initial and 3 additional recommendations
        generate_pdf(random_recommendations, additional_recommendations, preferred_day, start_time, end_time)
    else:
        messagebox.showinfo("No Results", "No results match your preferences.")


        
def select_one_recommendation(recommendations, root):
    top = tk.Toplevel(root)
    top.title("Select a Recommendation")

    selected_item_var = tk.StringVar()

    tk.Label(top, text="Select one of the following recommendations:").pack(padx=10, pady=10)
    title_menu = ttk.Combobox(top, textvariable=selected_item_var, values=recommendations, state="readonly")
    title_menu.pack(padx=5, pady=5)
    title_menu.current(0)

    def on_select():
        top.destroy()

    ttk.Button(top, text="Select", command=on_select).pack(pady=10)

    top.wait_window()  # Wait until the user selects an item
    return selected_item_var.get()  # Return the selected item


def display_schedule(day, start_time, end_time, recommendations, root, additional_recommendations=None):
    # Create a new window for the calendar
    calendar_window = tk.Toplevel(root)
    calendar_window.title("Weekly Schedule")

    # Days of the week
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Find the current day and start of the week
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # The start of the current week (Monday)

    # Display the week and the calendar
    for i, day_name in enumerate(days_of_week):
        current_day = start_of_week + timedelta(days=i)
        date_str = current_day.strftime("%d %b %Y")

        # Display each day of the week and the date
        label = tk.Label(calendar_window, text=f"{day_name} - {date_str}", font=("Arial", 10, "bold"))
        label.grid(row=0, column=i, padx=2, pady=2)

    # Display the preferred time slot on the selected day
    time_label = tk.Label(calendar_window, text=f"{start_time} - {end_time}", bg="lightgreen", font=("Arial", 10))
    col_index = days_of_week.index(day)
    time_label.grid(row=1, column=col_index, padx=2, pady=2)

    # Show the 5 initial recommendations
    tk.Label(calendar_window, text="Initial 5 Recommendations", font=("Arial", 9, "bold")).grid(row=2, column=col_index, padx=2, pady=2)

    # Show title, duration, and genres for each recommendation
    for i, rec in enumerate(recommendations):
        title_duration_genres = extract_title_duration_genres(rec)
        recommendation_label = tk.Label(calendar_window, text=title_duration_genres, bg="lightblue", font=("Arial", 8), justify='left')
        recommendation_label.grid(row=i + 3, column=col_index, padx=2, pady=2)

    # Separator between the 5 and the additional 3 recommendations
    if additional_recommendations:
        separator = tk.Label(calendar_window, text="You might also like...", font=("Arial", 9, "bold"))
        separator.grid(row=i + 4, column=col_index, padx=2, pady=5)

        for j, rec in enumerate(additional_recommendations):
            title_duration_genres = extract_title_duration_genres(rec)
            recommendation_label = tk.Label(calendar_window, text=title_duration_genres, bg="lightyellow", font=("Arial", 8))
            recommendation_label.grid(row=i + j + 5, column=col_index, padx=2, pady=2)

    return calendar_window


# Funzione per resettare i campi
def reset_fields(content_type_var, min_duration_var, max_duration_var, genre_var):
    content_type_var.set("Movie")
    min_duration_var.set(0)
    max_duration_var.set(200)
    genre_var.selection_clear(0, tk.END)
    
    
def create_ui(df):
    # Initialize the root window
    global root
    root = tk.Tk()
    root.title("Content Recommender")

    # Existing UI elements for content type, duration, and genres selection

    # Frame for selecting a content title for recommendations
    title_frame = tk.LabelFrame(root, text="Select a Title for Recommendations")
    title_frame.pack(fill="x", padx=5, pady=5)

    selected_title_var = tk.StringVar()
    titles = df['title'].tolist()  # List of all content titles
    title_menu = ttk.Combobox(title_frame, textvariable=selected_title_var, values=titles, state="readonly")
    title_menu.pack(padx=5, pady=5)
    title_menu.current(0)

    # Button to show recommendations based on the selected title
    recommendation_button = tk.Button(root, text="Show Recommendations", command=lambda: show_recommendations(df, selected_title_var.get()))
    recommendation_button.pack(pady=10)

    root.mainloop()


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
