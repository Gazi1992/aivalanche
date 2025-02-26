import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any

class Classifier:
    def __init__(self, seed: int = None, scale_data: bool = True, use_grid_search: bool = True):
        self.seed = seed
        self.scale_data = scale_data
        self.use_grid_search = use_grid_search
        self.classifiers = {
            'Decision Tree': DecisionTreeClassifier(random_state=seed),
            'Random Forest': RandomForestClassifier(random_state=seed),
            'SVM': SVC(random_state=seed),
            'KNN': KNeighborsClassifier(),
            # 'Neural Network': MLPClassifier(random_state=seed, max_iter=1000)
        }
        self.results = {}
        self.best_classifier = None
        self.scaler = StandardScaler()

    def add_classifier(self, name: str, classifier: Any) -> None:
        """Add a new classifier to the comparison."""
        self.classifiers[name] = classifier

    def remove_classifier(self, name: str) -> None:
        """Remove a classifier from the comparison."""
        if name in self.classifiers:
            del self.classifiers[name]

    def prepare_data(self, X: np.ndarray, y: np.ndarray,
                    test_size: float = 0.2) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Prepare data for training and testing."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.seed
        )

        if self.scale_data:
            X_train = self.scaler.fit_transform(X_train)
            X_test = self.scaler.transform(X_test)

        return X_train, X_test, y_train, y_test

    def train_and_evaluate(self, X: np.ndarray, y: np.ndarray,
                          test_size: float = 0.2, cv: int = 5) -> Dict:
        """Train and evaluate all classifiers with hyperparameter tuning."""
        X_train, X_test, y_train, y_test = self.prepare_data(X, y, test_size)

        # Define parameter grids for each classifier
        param_grids = {
            'Decision Tree': {
                'max_depth': [3, 5, 7, None],
                'min_samples_split': [2, 5, 10]
            },
            'Random Forest': {
                'n_estimators': [100, 200],
                'max_depth': [3, 5, None],
                'min_samples_split': [2, 5]
            },
            'SVM': {
                'C': [0.1, 1, 10],
                'kernel': ['rbf', 'linear']
            },
            'KNN': {
                'n_neighbors': [3, 5, 7],
                'weights': ['uniform', 'distance']
            },
            'Neural Network': {
                'hidden_layer_sizes': [(50,), (100,), (50, 50)],
                'alpha': [0.0001, 0.001],
                'activation': ['relu', 'tanh']
            }
        }

        for name, clf in self.classifiers.items():
            if self.use_grid_search:
                # Perform grid search
                grid_search = GridSearchCV(
                    clf,
                    param_grids[name],
                    cv=cv,
                    n_jobs=-1,
                    scoring='accuracy'
                )
                grid_search.fit(X_train, y_train)
                best_clf = grid_search.best_estimator_
                best_params = grid_search.best_params_
            else:
                # Train without grid search
                clf.fit(X_train, y_train)
                best_clf = clf
                best_params = None

            # Make predictions
            y_pred = best_clf.predict(X_test)

            # Store best classifier for future predictions
            self.classifiers[name] = best_clf

            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            cv_scores = cross_val_score(best_clf, X_train, y_train, cv=cv)

            self.results[name] = {
                'classifier': best_clf,
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'classification_report': classification_report(y_test, y_pred),
                'best_params': best_params
            }

        # Find best classifier
        self.best_classifier = max(self.results.items(),
                                 key=lambda x: x[1]['accuracy'])
        self.accuracy = self.best_classifier[1]['accuracy']

        return self.results

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using the best classifier."""
        if not self.best_classifier:
            raise ValueError("No best classifier available. Run train_and_evaluate first.")

        if self.scale_data:
            X = self.scaler.transform(X)

        return self.best_classifier[1]['classifier'].predict(X)

    def plot_results(self) -> None:
        """Plot comparison results."""
        if not self.results:
            raise ValueError("No results to plot. Run train_and_evaluate first.")

        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

        # Plot accuracies
        accuracies = [result['accuracy'] for result in self.results.values()]
        cv_means = [result['cv_mean'] for result in self.results.values()]
        cv_stds = [result['cv_std'] for result in self.results.values()]

        x = np.arange(len(self.classifiers))
        width = 0.35

        ax1.bar(x - width/2, accuracies, width, label='Test Accuracy')
        ax1.bar(x + width/2, cv_means, width, label='CV Mean Accuracy')
        ax1.set_ylabel('Accuracy')
        ax1.set_title('Classifier Comparison')
        ax1.set_xticks(x)
        ax1.set_xticklabels(self.classifiers.keys(), rotation=45)
        ax1.legend()

        # Plot confusion matrix for best classifier
        best_name = self.best_classifier[0]
        best_cm = self.results[best_name]['confusion_matrix']

        im = ax2.imshow(best_cm, interpolation='nearest', cmap=plt.cm.Blues)
        ax2.set_title(f'Confusion Matrix - {best_name}')

        # Add colorbar
        plt.colorbar(im, ax=ax2)

        # Add labels to confusion matrix
        thresh = best_cm.max() / 2
        for i in range(best_cm.shape[0]):
            for j in range(best_cm.shape[1]):
                ax2.text(j, i, format(best_cm[i, j], 'd'),
                        ha="center", va="center",
                        color="white" if best_cm[i, j] > thresh else "black")

        plt.tight_layout()
        plt.show()

    def get_best_classifier(self) -> Tuple[str, Dict]:
        """Return the best performing classifier and its results."""
        if not self.best_classifier:
            raise ValueError("No results available. Run train_and_evaluate first.")
        return self.best_classifier

    def print_results(self) -> None:
        """Print detailed results for all classifiers."""
        if not self.results:
            raise ValueError("No results to print. Run train_and_evaluate first.")

        for name, results in self.results.items():
            print(f"\n{'-'*50}")
            print(f"Classifier: {name}")
            print(f"Best Parameters: {results['best_params']}")
            print(f"Test Accuracy: {results['accuracy']:.4f}")
            print(f"CV Mean Accuracy: {results['cv_mean']:.4f} (+/- {results['cv_std']*2:.4f})")
            print("\nClassification Report:")
            print(results['classification_report'])

# Example usage:
if __name__ == "__main__":
    from sklearn.datasets import load_iris

    # Load data
    iris = load_iris()
    X, y = iris.data, iris.target

    # Create and run comparison with scaling enabled
    clf = Classifier(seed=42, scale_data=True)
    clf.train_and_evaluate(X, y)
    clf.print_results()
    clf.plot_results()

    # Create and run comparison with scaling disabled
    clf_no_scaling = Classifier(seed=42, scale_data=False)
    clf_no_scaling.train_and_evaluate(X, y)
    clf_no_scaling.print_results()
    clf_no_scaling.plot_results()
