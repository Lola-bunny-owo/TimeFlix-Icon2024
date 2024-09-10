from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from preprocessing import prepare_data_for_decision_tree
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

def train_decision_tree(df):
    # Prepara i dati per il Decision Tree
    X, y = prepare_data_for_decision_tree(df)

    # Dividi i dati in training e test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Inizializza il Decision Tree Classifier
    clf = DecisionTreeClassifier(class_weight='balanced', random_state=42)

    # Addestra il modello
    clf.fit(X_train, y_train)

    # Prevedi i dati di test
    y_pred = clf.predict(X_test)

    # Valuta il modello
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy}\n")
    print(classification_report(y_test, y_pred))
    
    # plot_decision_tree(clf)

    return clf

# Visualizza l'albero di decisione
def plot_decision_tree(clf):
    plt.figure(figsize=(20,10))
    plot_tree(clf, filled=True, feature_names=['PCA1', 'PCA2', 'PCA3', 'Film_Duration', 'Is_movie', 'Is_TVshow'], class_names=['Non-preferred', 'Preferred'], rounded=True)
    plt.savefig("output grafici/decision_tree_visualization.png")
    plt.show()

def predict_user_preference(df, clf):
    # Prepara i nuovi dati per la predizione
    X_new, _ = prepare_data_for_decision_tree(df)
    predictions = clf.predict(X_new)
    
    # Filtra i contenuti preferiti
    preferred_content = df[predictions == 1]
    
    if not preferred_content.empty:
        # Salva i contenuti preferiti in un file di testo
        preferred_content[['Title', 'user_preference']].to_csv('preferred_content_output.txt', encoding='utf-8', index=False)
        print("Preferred content saved to 'preferred_content_output.txt'.")
    
    return preferred_content