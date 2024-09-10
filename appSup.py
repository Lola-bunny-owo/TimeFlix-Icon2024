from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from preprocessing import prepare_data_for_decision_tree
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree 

# Funzione per addestrare un albero decisionale
def train_decision_tree(df, param_grid=None):
    X, y = prepare_data_for_decision_tree(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Usa GridSearchCV per ottimizzare i parametri
    if param_grid:
        grid_search = GridSearchCV(DecisionTreeClassifier(random_state=42), param_grid, cv=5)
        grid_search.fit(X_train, y_train)
        clf = grid_search.best_estimator_
        print(f"Best parameters: {grid_search.best_params_}")
    else:
        clf = DecisionTreeClassifier(class_weight='balanced', random_state=42, max_depth=5)
        clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

     # Valutazione
    print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
    print(classification_report(y_test, y_pred))

    # Visualizza l'albero decisionale
    plot_decision_tree(clf)

    return clf

def plot_decision_tree(clf):
    plt.figure(figsize=(20,10))
    plot_tree(clf, filled=True, feature_names=['PCA1', 'PCA2', 'PCA3', 'Film_Duration', 'Is_movie', 'Is_TVshow'], class_names=['Non-preferred', 'Preferred'], rounded=True)
    plt.savefig("output grafici/decision_tree_visualization.png")
    plt.show()

# Funzione per le preferenze dell'utente
def predict_user_preference(df, clf):
    X_new, _ = prepare_data_for_decision_tree(df)
    predictions = clf.predict(X_new)
    preferred_content = df[predictions == 1]

    if not preferred_content.empty:
        preferred_content[['Title', 'user_preference']].to_csv('preferred_content_output.txt', encoding='utf-8', index=False)
        print("Preferred content saved to 'preferred_content_output.txt'.")
    
    return preferred_content
