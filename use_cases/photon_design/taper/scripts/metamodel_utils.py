import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import itertools
from tqdm import tqdm
import optuna
from optuna.trial import Trial

class Simulation_dataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class NN_metamodel(nn.Module):
    def __init__(self, input_size, layer_sizes, dropout_rate=0.1, use_layer_norm=True):
        super(NN_metamodel, self).__init__()

        layers = []
        prev_size = input_size

        for size in layer_sizes:
            layers.append(nn.Linear(prev_size, size))
            if use_layer_norm:
                layers.append(nn.LayerNorm(size))
            layers.extend([
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_size = size

        layers.append(nn.Linear(prev_size, 1))
        self.network = nn.Sequential(*layers)
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.kaiming_normal_(module.weight, nonlinearity='relu')
            if module.bias is not None:
                nn.init.zeros_(module.bias)

    def forward(self, x):
        return self.network(x)

def prepare_data(df, target_column, test_size=0.2, batch_size=32):
    """
    Prepare data for training
    """
    # Separate features and target
    X = df.drop(columns=[target_column])
    y = df[target_column]

    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=test_size, random_state=42
    )

    # Create datasets
    train_dataset = Simulation_dataset(X_train, y_train.values.reshape(-1, 1))
    test_dataset = Simulation_dataset(X_test, y_test.values.reshape(-1, 1))

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    return train_loader, test_loader, scaler

def objective(trial: Trial, df: pd.DataFrame, target_column: str):
    """
    Optuna objective function for hyperparameter optimization
    """
    # Define hyperparameters to optimize
    n_layers = trial.suggest_int('n_layers', 1, 4)
    layer_sizes = []
    for i in range(n_layers):
        layer_sizes.append(trial.suggest_int(f'layer_{i}_size', 16, 256))

    params = {
        'learning_rate': trial.suggest_float('learning_rate', 1e-4, 1e-2, log=True),
        'batch_size': trial.suggest_categorical('batch_size', [16, 32, 64, 128]),
        'dropout_rate': trial.suggest_float('dropout_rate', 0.0, 0.5),
        'use_layer_norm': trial.suggest_categorical('use_layer_norm', [True, False]),
        'num_epochs': trial.suggest_int('num_epochs', 30, 100)
    }

    # Prepare data
    X = df.drop(columns=[target_column])
    y = df[target_column]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # Create datasets and dataloaders
    train_dataset = Simulation_dataset(X_train, y_train.values.reshape(-1, 1))
    test_dataset = Simulation_dataset(X_test, y_test.values.reshape(-1, 1))

    train_loader = DataLoader(train_dataset, batch_size=params['batch_size'], shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=params['batch_size'])

    # Create and train model
    model = NN_metamodel(
        input_size=X.shape[1],
        layer_sizes=layer_sizes,
        dropout_rate=params['dropout_rate'],
        use_layer_norm=params['use_layer_norm']
    )

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=params['learning_rate'])

    # Training loop with early stopping
    best_test_loss = float('inf')
    patience = 5
    patience_counter = 0

    for epoch in range(params['num_epochs']):
        model.train()
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            y_pred = model(X_batch)
            loss = criterion(y_pred, y_batch)
            loss.backward()
            optimizer.step()

        # Evaluate on test set
        model.eval()
        test_loss = 0
        with torch.no_grad():
            for X_batch, y_batch in test_loader:
                y_pred = model(X_batch)
                test_loss += criterion(y_pred, y_batch).item()

        test_loss /= len(test_loader)

        # Report intermediate value
        trial.report(test_loss, epoch)

        # Early stopping
        if test_loss < best_test_loss:
            best_test_loss = test_loss
            patience_counter = 0
        else:
            patience_counter += 1

        if patience_counter >= patience:
            break

        # Handle pruning based on the intermediate value
        if trial.should_prune():
            raise optuna.TrialPruned()

    return best_test_loss

def optimize_hyperparameters(df, target_column, n_trials=100):
    """
    Run hyperparameter optimization using Optuna
    """
    study = optuna.create_study(
        direction="minimize",
        pruner=optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=10),
        sampler=optuna.samplers.TPESampler(seed=42)
    )

    study.optimize(
        lambda trial: objective(trial, df, target_column),
        n_trials=n_trials,
        show_progress_bar=True
    )

    # Print optimization results
    print("\nBest trial:")
    trial = study.best_trial

    print(f"Value (MSE): {trial.value:.6f}")
    print("\nBest hyperparameters:")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")

    # Plot optimization history
    plt.figure(figsize=(10, 6))
    optuna.visualization.matplotlib.plot_optimization_history(study)
    plt.title("Optimization History")
    plt.show()

    # Plot parameter importances
    plt.figure(figsize=(10, 6))
    optuna.visualization.matplotlib.plot_param_importances(study)
    plt.title("Parameter Importances")
    plt.show()

    return study.best_params, study.best_value

def create_best_model(df, target_column, best_params):
    """
    Create and train model with the best parameters found
    """
    # Extract layer sizes from best parameters
    n_layers = best_params['n_layers']
    layer_sizes = [best_params[f'layer_{i}_size'] for i in range(n_layers)]

    # Prepare data
    X = df.drop(columns=[target_column])
    y = df[target_column]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    train_dataset = Simulation_dataset(X_train, y_train.values.reshape(-1, 1))
    test_dataset = Simulation_dataset(X_test, y_test.values.reshape(-1, 1))

    train_loader = DataLoader(train_dataset, batch_size=best_params['batch_size'], shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=best_params['batch_size'])

    # Create model with best parameters
    model = NN_metamodel(
        input_size=X.shape[1],
        layer_sizes=layer_sizes,
        dropout_rate=best_params['dropout_rate'],
        use_layer_norm=best_params['use_layer_norm']
    )

    # Train and evaluate
    train_and_evaluate(
        model,
        train_loader,
        test_loader,
        num_epochs=best_params['num_epochs'],
        learning_rate=best_params['learning_rate']
    )

    return model, train_loader, test_loader

def create_layer_configurations(min_layers, max_layers, possible_sizes):
    """
    Generate different layer configurations
    """
    configs = []
    for num_layers in range(min_layers, max_layers + 1):
        configs.extend(list(itertools.product(possible_sizes, repeat = num_layers)))
    return [list(config) for config in configs]

def evaluate_model(model, data_loader):
    """
    Evaluate model performance using MSE and R² metrics
    """
    model.eval()
    true_values = []
    predictions = []

    with torch.no_grad():
        for X_batch, y_batch in data_loader:
            y_pred = model(X_batch)
            predictions.extend(y_pred.numpy().flatten())
            true_values.extend(y_batch.numpy().flatten())

    predictions = np.array(predictions)
    true_values = np.array(true_values)

    return {
        'mse': mean_squared_error(true_values, predictions),
        'r2': r2_score(true_values, predictions)
    }

def train_model(model, train_loader, test_loader, num_epochs=100, learning_rate=0.001, verbose=True):
    """
    Train the neural network
    """
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    train_losses = []
    test_losses = []

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            y_pred = model(X_batch)
            loss = criterion(y_pred, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        test_loss = 0
        with torch.no_grad():
            for X_batch, y_batch in test_loader:
                y_pred = model(X_batch)
                test_loss += criterion(y_pred, y_batch).item()

        train_losses.append(train_loss / len(train_loader))
        test_losses.append(test_loss / len(test_loader))

        if verbose and (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Train Loss: {train_losses[-1]:.4f}, Test Loss: {test_losses[-1]:.4f}')

    return train_losses, test_losses

def plot_training_loss(train_losses, test_losses):
    """
    Plot training and test loss curves
    """
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(test_losses, label='Test Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Test Loss Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_prediction_accuracy(model, train_loader, test_loader):
    """
    Create a scatter plot of predicted vs true values
    """
    model.eval()

    # Lists to store predictions and true values
    train_predictions = []
    train_true = []
    test_predictions = []
    test_true = []

    # Gather predictions for training data
    with torch.no_grad():
        for X_batch, y_batch in train_loader:
            pred = model(X_batch)
            train_predictions.extend(pred.numpy().flatten())
            train_true.extend(y_batch.numpy().flatten())

    # Gather predictions for test data
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            pred = model(X_batch)
            test_predictions.extend(pred.numpy().flatten())
            test_true.extend(y_batch.numpy().flatten())

    # Convert to numpy arrays
    train_predictions = np.array(train_predictions)
    train_true = np.array(train_true)
    test_predictions = np.array(test_predictions)
    test_true = np.array(test_true)

    # Calculate min and max for plot limits
    min_val = min(min(train_true), min(test_true))
    max_val = max(max(train_true), max(test_true))

    # Create the plot
    plt.figure(figsize=(10, 10))

    # Plot training data
    plt.scatter(train_true, train_predictions,
               alpha=0.5, label='Training Data',
               color='blue')

    # Plot test data
    plt.scatter(test_true, test_predictions,
               alpha=0.5, label='Test Data',
               color='red')

    # Plot diagonal line (perfect predictions)
    plt.plot([min_val, max_val], [min_val, max_val],
             'k--', label='Perfect Prediction')

    plt.xlabel('True Values')
    plt.ylabel('Predicted Values')
    plt.title('Prediction Accuracy: True vs Predicted Values')
    plt.legend()
    plt.grid(True)

    # Make the plot square
    plt.axis('square')

    # Set equal limits for both axes
    plt.xlim(min_val, max_val)
    plt.ylim(min_val, max_val)

    plt.show()

def hyperparameter_tuning(df, target_column, param_grid):
    """
    Perform grid search for hyperparameter tuning
    """
    param_combinations = [dict(zip(param_grid.keys(), v))
                         for v in itertools.product(*param_grid.values())]

    all_results = []
    best_test_mse = float('inf')
    best_params = None
    best_model = None

    input_size = len(df.columns) - 1

    for params in tqdm(param_combinations, desc="Trying parameter combinations"):
        # Prepare data with current batch size
        train_loader, test_loader, scaler = prepare_data(
            df,
            target_column,
            test_size=0.2,
            batch_size=params['batch_size']
        )

        # Create model with current architecture
        model = NN_metamodel(
            input_size=input_size,
            layer_sizes=params['layer_configs'],
            dropout_rate=params['dropout_rate'],
            use_layer_norm=params['use_layer_norm']
        )

        # Train model
        train_losses, test_losses = train_model(
            model,
            train_loader,
            test_loader,
            num_epochs=params['num_epochs'],
            learning_rate=params['learning_rate'],
            verbose=False
        )

        # Evaluate model
        train_metrics = evaluate_model(model, train_loader)
        test_metrics = evaluate_model(model, test_loader)

        # Store results
        result = {
            **params,
            'num_layers': len(params['layer_configs']),
            'architecture': str(params['layer_configs']),
            'train_mse': train_metrics['mse'],
            'train_r2': train_metrics['r2'],
            'test_mse': test_metrics['mse'],
            'test_r2': test_metrics['r2'],
            'final_train_loss': train_losses[-1],
            'final_test_loss': test_losses[-1]
        }
        all_results.append(result)

        # Update best model if current one is better
        if test_metrics['mse'] < best_test_mse:
            best_test_mse = test_metrics['mse']
            best_params = params.copy()
            best_model = model

    # Convert results to DataFrame
    results_df = pd.DataFrame(all_results)

    # Sort results by test MSE
    results_df = results_df.sort_values('test_mse')

    # Print best parameters
    print("\nBest architecture found:")
    print(f"Number of layers: {len(best_params['layer_configs'])}")
    print(f"Layer sizes: {best_params['layer_configs']}")
    print(f"Layer normalization: {best_params['use_layer_norm']}")
    print(f"\nOther parameters:")
    for param, value in best_params.items():
        if param not in ['layer_configs', 'use_layer_norm']:
            print(f"{param}: {value}")
    print(f"\nBest test MSE: {best_test_mse:.6f}")
    print(f"Best test R²: {results_df.iloc[0]['test_r2']:.6f}")

    return best_params, results_df, best_model

def train_and_evaluate(model, train_loader, test_loader, num_epochs=100, learning_rate=0.001):
    """
    Train the model and visualize results
    """
    # Train the model
    train_losses, test_losses = train_model(
        model, train_loader, test_loader,
        num_epochs=num_epochs, learning_rate=learning_rate
    )

    # Plot the training loss
    plot_training_loss(train_losses, test_losses)

    # Plot prediction accuracy
    plot_prediction_accuracy(model, train_loader, test_loader)

    return train_losses, test_losses

# Example usage
if __name__ == "__main__":
    # Generate layer configurations
    layer_configs = create_layer_configurations(
        min_layers=2,
        max_layers=4,
        possible_sizes=[32, 64, 128]
    )

    # Define parameter grid
    param_grid = {
        'layer_configs': layer_configs,
        'learning_rate': [0.001, 0.01],
        'batch_size': [16, 32, 64],
        'num_epochs': [50, 100],
        'dropout_rate': [0.1, 0.2],
        'use_layer_norm': [True, False]
    }

    # Load your data
    # df = pd.read_csv('your_simulation_data.csv')
    # target_column = 'your_target_column'

    # Perform hyperparameter tuning
    # best_params, results_df, best_model = hyperparameter_tuning(df, target_column, param_grid)

    # Train final model with best parameters and visualize results
    # train_loader, test_loader, scaler = prepare_data(
    #     df,
    #     target_column,
    #     batch_size=best_params['batch_size']
    # )

    # Visualize the results with the best model
    # train_and_evaluate(best_model, train_loader, test_loader)

    # Compare performance with and without layer norm
    # norm_results = results_df.groupby('use_layer_norm')[['test_mse', 'test_r2']].mean()
    # print("\nAverage performance comparison:")
    # print(norm_results)
