from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_validate
from sklearn.metrics import classification_report
import numpy as np
from preprocessing import prepare_data_for_decision_tree

def train_decision_tree_with_cv(df, cv=5):
    # Prepara i dati per il Decision Tree
    X, y = prepare_data_for_decision_tree(df)

    # Definisci il modello di base
    clf = DecisionTreeClassifier(class_weight='balanced', random_state=42)

    # Esegui la cross-validation e calcola le metriche
    scoring = ['accuracy', 'precision', 'recall', 'f1']
    cv_results = cross_validate(clf, X, y, cv=cv, scoring=scoring, return_train_score=False)

    # Calcola media e deviazione standard delle metriche
    mean_scores = {metric: np.mean(cv_results[f'test_{metric}']) for metric in scoring}
    std_scores = {metric: np.std(cv_results[f'test_{metric}']) for metric in scoring}

    # Stampa i risultati
    print("Risultati Cross-Validation per gli Alberi Decisionali, con k=5 folds:")
    print(f"Accuratezza Media: {mean_scores['accuracy']:.3f} +- {std_scores['accuracy']:.3f}")
    print(f"Precisione Media: {mean_scores['precision']:.3f} +- {std_scores['precision']:.3f}")
    print(f"Recall Media: {mean_scores['recall']:.3f} +- {std_scores['recall']:.3f}")
    print(f"F1 Score Medio: {mean_scores['f1']:.3f} +- {std_scores['f1']:.3f}")

    # Addestra il modello sull'intero dataset per ottenere il modello finale
    clf.fit(X, y)
    print("\nReport di Classificazione sull'Intero Set di Training:\n")
    print(classification_report(y, clf.predict(X)))

    return clf, mean_scores, std_scores

# Funzione di predizione delle preferenze dell'utente
def predict_user_preference(df, clf):
    # Prepara i dati per la predizione
    X_new, _ = prepare_data_for_decision_tree(df)
    predictions = clf.predict(X_new)
    
    # Filtra i contenuti preferiti
    preferred_content = df[predictions == 1]
    
    if not preferred_content.empty:
        # Salva i contenuti preferiti in un file di testo
        preferred_content[['Title', 'user_preference']].to_csv('preferred_content_output.txt', encoding='utf-8', index=False)
    
    return preferred_content