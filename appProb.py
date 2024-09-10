import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from preprocessing import convert_time_to_minutes, convert_minutes_to_time

# Addestramento del modello Naive Bayes
def train_naive_bayes(X, y):
    
    # Suddividi i dati in set di training e test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Inizializza e addestra il modello
    model = GaussianNB()
    model.fit(X_train, y_train)
    
    # Stampa il numero di campioni usati per l'addestramento e il test
    print(f"\nModello addestrato su {len(X_train)} campioni.")
    print(f"Testato su {len(X_test)} campioni.")
    
    # Predizione sui dati di test
    y_pred = model.predict(X_test)
    
    # Calcola e stampa le metriche di valutazione
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nPerformance del modello:")
    print(f"Accuracy: {accuracy:.4f}")
    print(classification_report(y_test, y_pred))
    
    return model
    

# Funzione di predizione del momento migliore per guardare contenuti
def predict_best_time(model, le_day):
    
    # Si prepara un dataframe con tutte le combinazioni possibili di giorni e orari
    days = le_day.classes_
    times = pd.date_range('10:00', '23:00', freq='1h').strftime('%H:%M')  
    
    # Crea una lista di tutte le combinazioni di giorno e orario di inizio e fine
    combinations = [(day, start_time, end_time) for day in days for start_time in times for end_time in times if end_time > start_time]

    # Convertiamo in DataFrame
    df_combinations = pd.DataFrame(combinations, columns=['Day', 'Start_Time', 'End_Time'])
    df_combinations['Day_Encoded'] = le_day.transform(df_combinations['Day'])
    df_combinations['Start_Time'] = df_combinations['Start_Time'].apply(convert_time_to_minutes)
    df_combinations['End_Time'] = df_combinations['End_Time'].apply(convert_time_to_minutes)
    
    # Predizione per tutte le combinazioni - il modello predice per ogni combinazione se quel giorno e orario è preferito
    predictions = model.predict(df_combinations[['Day_Encoded', 'Start_Time', 'End_Time']])
    
    # Aggiungiamo le predizioni al DataFrame
    df_combinations['Prediction'] = predictions
    
    # Filtra solo le combinazioni con predizione positiva
    positive_combinations = df_combinations[df_combinations['Prediction'] == 1]
    
    # Stampa solo le combinazioni con Prediction == 1 per capire quali sono considerate preferite
    print("\nCombinazioni con Prediction == 1: ")
    
    if not positive_combinations.empty:
        print("\nCombinazioni positive (tempo preferito): ")
        print(positive_combinations.head(10))
        
        # Trova la prima combinazione positiva per il giorno e l'intervallo di tempo migliore
        best_combination = positive_combinations.sort_values(by=['Day', 'Start_Time']).iloc[0]
        best_start_time = convert_minutes_to_time(best_combination['Start_Time'])
        best_end_time = convert_minutes_to_time(best_combination['End_Time'])
        return best_combination['Day'], best_start_time, best_end_time
    else:
        print("Nessuna combinazione positiva trovata. Il modello potrebbe non aver appreso correttamente le preferenze.")
        return "N/A", "N/A", "N/A"
