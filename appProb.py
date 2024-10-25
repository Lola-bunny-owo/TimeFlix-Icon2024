import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_validate
from sklearn.metrics import classification_report
from preprocessing import convert_time_to_minutes, convert_minutes_to_time

# Addestramento del modello Naive Bayes
def train_naive_bayes_with_cv(X, y, cv=10):
    
    # Inizializza e addestra il modello
    model = GaussianNB()
    
    # Si definiscono le metriche, si esegue la c-v e si calcolano le metriche.
    scoring = ['accuracy', 'precision', 'recall', 'f1']
    cv_results = cross_validate(model, X, y, cv=cv, scoring=scoring, return_train_score=False)
    
    # Calcola media e deviazione standard delle metriche
    mean_scores = {metric: np.mean(cv_results[f'test_{metric}']) for metric in scoring}
    std_scores = {metric: np.std(cv_results[f'test_{metric}']) for metric in scoring}
    
    # Stampa i risultati
    print("\nRisultati Cross-Validation per il Naive Bayes, con k=10 folds:")
    print(f"Accuratezza Media: {mean_scores['accuracy']:.3f} +- {std_scores['accuracy']:.3f}")
    print(f"Precisione Media: {mean_scores['precision']:.3f} +- {std_scores['precision']:.3f}")
    print(f"Recall Media: {mean_scores['recall']:.3f} +- {std_scores['recall']:.3f}")
    print(f"F1 Score Medio: {mean_scores['f1']:.3f} +- {std_scores['f1']:.3f}")
    
    # Addestra il modello sull'intero dataset per ottenere il modello finale
    model.fit(X, y)
    print("\nReport di Classificazione sull'Intero Set di Training:\n")
    print(classification_report(y, model.predict(X)))

    return model, mean_scores, std_scores    

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
