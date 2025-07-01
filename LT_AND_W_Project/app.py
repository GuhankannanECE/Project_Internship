import numpy as np
import json
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Define cavity resonator with physical parameters
class CavityResonator:
    def __init__(self, shape, material):
        self.shape = shape
        self.material = material
        self.resonant_frequency = None
        self.quality_factor = None
    
    # Calculate theoretical resonant frequency for rectangular cavity
    def calculate_resonant_frequency(self, length, width, height, mode=(1,0,1)):
        """
        Calculate resonant frequency for a rectangular cavity using formula:
        f = (c/2) * sqrt((m/a)^2 + (n/b)^2 + (p/c)^2)
        where c is speed of light, a,b,c are dimensions, and m,n,p are mode numbers
        """
        c = 3e8  # speed of light in m/s
        m, n, p = mode
        
        # Convert dimensions to meters
        a, b, c_dim = length, width, height
        
        # Calculate resonant frequency
        f = (c/2) * np.sqrt((m/a)**2 + (n/b)**2 + (p/c_dim)**2)
        return f / 1e9  # Convert to GHz
    
    # Calculate quality factor based on material properties and dimensions
    def calculate_quality_factor(self, length, width, height, conductivity, surface_roughness):
        """
        Calculate Q factor using simplified formula based on cavity volume, 
        surface area, material conductivity, and surface roughness
        """
        # Cavity volume and surface area
        volume = length * width * height
        surface_area = 2 * (length*width + length*height + width*height)
        
        # Skin depth at ~2.4 GHz (approximation)
        f = 2.4e9  # Reference frequency in Hz
        mu = 4 * np.pi * 1e-7  # Permeability of free space
        skin_depth = np.sqrt(2 / (2 * np.pi * f * mu * conductivity))
        
        # Surface resistance including roughness effect
        roughness_factor = 1+ (2 / np.pi) * np.arctan(1.4 * (surface_roughness / skin_depth)**2)
        R_s = roughness_factor / (skin_depth * conductivity)
        
        # Q factor calculation (simplified model)
        Q = (2*np.pi * f * mu * volume) / (R_s * surface_area)
        
        return Q

# Generate training data based on physical parameters
def generate_training_data(num_samples):
    # Generate random physical parameters within reasonable ranges
    length = np.random.uniform(0.05, 0.2, num_samples)  # 5-20 cm
    width = np.random.uniform(0.02, 0.1, num_samples)   # 2-10 cm
    height = np.random.uniform(0.02, 0.1, num_samples)  # 2-10 cm
    conductivity = np.random.uniform(1e6, 6e7, num_samples)  # Conductivity in S/m (copper ~5.8e7)
    surface_roughness = np.random.uniform(0.1e-6, 10e-6, num_samples)  # 0.1-10 µm
    
    # Create input array
    X = np.column_stack((length, width, height, conductivity, surface_roughness))
    
    # Initialize output array
    y = np.zeros((num_samples, 2))
    
    # Create a resonator instance for calculations
    resonator = CavityResonator('rectangular', 'metal')
    
    # Calculate resonant frequency and Q factor for each sample
    for i in range(num_samples):
        y[i, 0] = resonator.calculate_resonant_frequency(
            X[i, 0], X[i, 1], X[i, 2])
        y[i, 1] = resonator.calculate_quality_factor(
            X[i, 0], X[i, 1], X[i, 2], X[i, 3], X[i, 4])
    
    # Add some noise to simulate measurement/modeling error
    y[:, 0] += np.random.normal(0, 0.05, num_samples)  # ~50 MHz noise
    y[:, 1] += np.random.normal(0, y[:, 1] * 0.05, num_samples)  # 5% noise
    
    return X, y

# Function to normalize parameters to 0-1 range for optimization
def normalize_parameters(params, param_ranges):
    normalized = np.zeros_like(params)
    for i in range(params.shape[1]):
        min_val, max_val = param_ranges[i]
        normalized[:, i] = (params[:, i] - min_val) / (max_val - min_val)
    return normalized

# Function to denormalize parameters from 0-1 range to actual values
def denormalize_parameters(normalized_params, param_ranges):
    denormalized = np.zeros_like(normalized_params)
    for i in range(normalized_params.shape[1]):
        min_val, max_val = param_ranges[i]
        denormalized[:, i] = normalized_params[:, i] * (max_val - min_val) + min_val
    return denormalized

# Define parameter ranges
param_ranges = [
    (0.05, 0.2),     # length: 5-20 cm
    (0.02, 0.1),     # width: 2-10 cm
    (0.02, 0.1),     # height: 2-10 cm
    (1e6, 6e7),      # conductivity: 1-60 MS/m
    (0.1e-6, 10e-6)  # surface roughness: 0.1-10 µm
]

# Train the ML model
def train_ml_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalize the input parameters
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = MLPRegressor(
        hidden_layer_sizes=(128, 64, 32),  # Increased complexity for physical model
        activation='relu',
        solver='adam',
        alpha=0.0001,
        learning_rate_init=0.001,
        max_iter=500,
        random_state=42,
        verbose=False
    )
    
    model.fit(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    
    return model, scaler, test_score, X_test, y_test

# Generate a plot as base64 image (unchanged from original)
def get_plot_as_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return img_base64

# Create plots for model performance (unchanged from original)
def create_model_performance_plot(model, X_test_scaled, y_test):
    y_pred = model.predict(X_test_scaled)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot predictions vs. actual for frequency
    axes[0].scatter(y_test[:, 0], y_pred[:, 0], alpha=0.5, color='royalblue')
    min_val = min(y_test[:, 0].min(), y_pred[:, 0].min()) * 0.9
    max_val = max(y_test[:, 0].max(), y_pred[:, 0].max()) * 1.1
    axes[0].plot([min_val, max_val], [min_val, max_val], 'k--')
    axes[0].set_xlabel('Actual Frequency (GHz)')
    axes[0].set_ylabel('Predicted Frequency (GHz)')
    axes[0].set_title('Model Performance - Frequency Prediction')
    
    # Plot predictions vs. actual for Q factor
    axes[1].scatter(y_test[:, 1], y_pred[:, 1], alpha=0.5, color='coral')
    min_val = min(y_test[:, 1].min(), y_pred[:, 1].min()) * 0.9
    max_val = max(y_test[:, 1].max(), y_pred[:, 1].max()) * 1.1
    axes[1].plot([min_val, max_val], [min_val, max_val], 'k--')
    axes[1].set_xlabel('Actual Q Factor')
    axes[1].set_ylabel('Predicted Q Factor')
    axes[1].set_title('Model Performance - Q Factor Prediction')
    
    plt.tight_layout()
    return get_plot_as_base64(fig)

# Modified auto-tuning function to work with physical parameters
def auto_tune(target_freq, target_q, model, scaler, max_iterations=100):
    # Start with random normalized parameters
    best_params_norm = np.random.rand(1, 5)
    best_error = float('inf')
    
    # Store optimization history
    history = {
        'iterations': [],
        'best_params': [],
        'predicted_freq': [],
        'predicted_q': [],
        'freq_error': [],
        'q_error': [],
        'total_error': []
    }
    
    for i in range(max_iterations):
        # Create random variations of current best parameters (in normalized space)
        candidate_params_norm = best_params_norm + np.random.normal(0, 0.1, (10, 5))
        candidate_params_norm = np.clip(candidate_params_norm, 0, 1)
        
        # Evaluate candidates
        candidate_params_scaled = scaler.transform(
            denormalize_parameters(candidate_params_norm, param_ranges))
        predicted_outputs = model.predict(candidate_params_scaled)
        
        # Calculate errors
        freq_errors = np.abs(predicted_outputs[:, 0] - target_freq)
        q_errors = np.abs(predicted_outputs[:, 1] - target_q)
        
        # Normalized errors (as percentage of target)
        normalized_freq_errors = freq_errors / target_freq
        normalized_q_errors = q_errors / target_q
        
        # Total error with weighting
        # Can adjust weights based on importance
        freq_weight = 1.0
        q_weight = 1.0
        total_errors = freq_weight * normalized_freq_errors + q_weight * normalized_q_errors
        
        # Find best candidate
        best_candidate_idx = np.argmin(total_errors)
        candidate_error = total_errors[best_candidate_idx]
        
        # Update if better than current best
        if candidate_error < best_error:
            best_error = candidate_error
            best_params_norm = candidate_params_norm[best_candidate_idx:best_candidate_idx+1]
            
            # Convert normalized parameters to actual physical values
            best_params_physical = denormalize_parameters(best_params_norm, param_ranges)[0]
            
            # Record for history
            history['iterations'].append(i)
            history['best_params'].append(best_params_physical.tolist())
            history['predicted_freq'].append(float(predicted_outputs[best_candidate_idx, 0]))
            history['predicted_q'].append(float(predicted_outputs[best_candidate_idx, 1]))
            history['freq_error'].append(float(normalized_freq_errors[best_candidate_idx]))
            history['q_error'].append(float(normalized_q_errors[best_candidate_idx]))
            history['total_error'].append(float(candidate_error))
            
            # Check if close enough to target
            if best_error < 0.01:
                break
    
    # Get final prediction
    best_params_physical = denormalize_parameters(best_params_norm, param_ranges)[0]
    final_prediction = model.predict(scaler.transform(best_params_physical.reshape(1, -1)))
    
    # Create parameter descriptions with units
    param_descriptions = [
        f"Length: {best_params_physical[0]:.3f} m",
        f"Width: {best_params_physical[1]:.3f} m",
        f"Height: {best_params_physical[2]:.3f} m",
        f"Conductivity: {best_params_physical[3]:.2e} S/m",
        f"Surface Roughness: {best_params_physical[4]:.2e} m"
    ]
    
    result = {
        'optimal_params': best_params_physical.tolist(),
        'param_descriptions': param_descriptions,
        'resonant_frequency': float(final_prediction[0, 0]),
        'quality_factor': float(final_prediction[0, 1]),
        'history': history
    }
    
    return result

# Create optimization progress plots (modified to show physical parameters)
def create_optimization_plots(history, target_freq, target_q):
    # Convert lists for easier plotting
    iterations = history['iterations']
    predicted_freq = history['predicted_freq']
    predicted_q = history['predicted_q']
    freq_error = history['freq_error']
    q_error = history['q_error']
    total_error = history['total_error']
    
    # Create progress plots
    fig, axes = plt.subplots(2, 2, figsize=(18, 10))
    fig.suptitle('Cavity Resonator Optimization Progress', fontsize=16)
    
    # Plot frequency convergence
    axes[0, 0].plot(iterations, predicted_freq, 'o-', color='royalblue')
    axes[0, 0].axhline(y=target_freq, color='r', linestyle='--', label=f'Target: {target_freq} GHz')
    axes[0, 0].set_xlabel('Iteration')
    axes[0, 0].set_ylabel('Predicted Frequency (GHz)')
    axes[0, 0].set_title('Frequency Convergence')
    axes[0, 0].legend()
    
    # Plot Q factor convergence
    axes[0, 1].plot(iterations, predicted_q, 'o-', color='coral')
    axes[0, 1].axhline(y=target_q, color='r', linestyle='--', label=f'Target: {target_q}')
    axes[0, 1].set_xlabel('Iteration')
    axes[0, 1].set_ylabel('Predicted Q Factor')
    axes[0, 1].set_title('Q Factor Convergence')
    axes[0, 1].legend()
    
    # Plot error convergence
    axes[1, 0].plot(iterations, freq_error, 'o-', color='blue', label='Frequency Error')
    axes[1, 0].plot(iterations, q_error, 'o-', color='red', label='Q Factor Error')
    axes[1, 0].plot(iterations, total_error, 'o-', color='black', label='Total Error')
    axes[1, 0].set_xlabel('Iteration')
    axes[1, 0].set_ylabel('Normalized Error')
    axes[1, 0].set_title('Error Convergence')
    axes[1, 0].set_yscale('log')
    axes[1, 0].legend()
    
    # Plot parameter evolution if we have parameter history
    if 'best_params' in history and history['best_params']:
        # Extract the evolution of each parameter
        param_history = np.array(history['best_params'])
        
        # Only plot the first three parameters for clarity (dimensions)
        param_names = ['Length (m)', 'Width (m)', 'Height (m)']
        for i in range(3):  # Plot only dimensions for clarity
            axes[1, 1].plot(iterations, param_history[:, i], 'o-', label=param_names[i])
        
        axes[1, 1].set_xlabel('Iteration')
        axes[1, 1].set_ylabel('Parameter Value (m)')
        axes[1, 1].set_title('Parameter Evolution (Dimensions)')
        axes[1, 1].legend()
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    return get_plot_as_base64(fig)

# Create final results plots (modified for physical parameters)
def create_final_results_plot(param_descriptions, final_prediction, target_freq, target_q):
    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Final Cavity Resonator Tuning Results', fontsize=16)
    
    # Bar chart of optimal parameters - simplified to show dimensions only
    axes[0].axis('off')  # Turn off the axis
    
    # Create a table to display parameters
    param_table = axes[0].table(
        cellText=[[desc] for desc in param_descriptions],
        loc='center',
        cellLoc='left',
        colWidths=[0.8]
    )
    param_table.auto_set_font_size(False)
    param_table.set_fontsize(10)
    param_table.scale(1, 1.5)
    
    # Title for the table
    axes[0].set_title('Optimal Cavity Parameters')
    
    # Comparison of target vs. achieved
    metrics = ['Frequency (GHz)', 'Q Factor']
    target_values = [target_freq, target_q]
    achieved_values = [final_prediction[0], final_prediction[1]]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    axes[1].bar(x - width/2, target_values, width, label='Target', color='coral')
    axes[1].bar(x + width/2, achieved_values, width, label='Achieved', color='royalblue')
    
    # Add percentage difference
    for i in range(len(metrics)):
        diff_pct = (achieved_values[i] - target_values[i]) / target_values[i] * 100
        axes[1].text(i, max(target_values[i], achieved_values[i]) * 1.05, 
                 f"{diff_pct:+.2f}%", ha='center')
    
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(metrics)
    axes[1].legend()
    axes[1].set_title('Target vs. Achieved Performance')
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    return get_plot_as_base64(fig)

# Global variables to store the model and scaler
global_model = None
global_scaler = None
global_X_test = None
global_y_test = None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/train', methods=['POST'])
def train_model():
    global global_model, global_scaler, global_X_test, global_y_test
    
    samples = int(request.form.get('samples', 5000))
    
    # Generate data and train model
    X, y = generate_training_data(samples)
    model, scaler, test_score, X_test, y_test = train_ml_model(X, y)
    
    global_model = model
    global_scaler = scaler
    global_X_test = X_test
    global_y_test = y_test
    
    # Generate model performance plot
    model_plot = create_model_performance_plot(model, scaler.transform(X_test), y_test)
    
    # Calculate mean values for interpretability
    mean_freq = np.mean(y[:, 0])
    mean_q = np.mean(y[:, 1])
    
    return jsonify({
        'status': 'success',
        'message': f'Model trained successfully with {samples} samples',
        'test_score': float(test_score),
        'mean_freq': float(mean_freq),
        'mean_q': float(mean_q),
        'model_plot': model_plot
    })

@app.route('/tune', methods=['POST'])
def tune_cavity():
    global global_model, global_scaler
    
    if global_model is None or global_scaler is None:
        return jsonify({
            'status': 'error',
            'message': 'Please train the model first'
        })
    
    # Get tuning targets from form
    target_freq = float(request.form.get('target_freq', 2.4))
    target_q = float(request.form.get('target_q', 10000))
    iterations = int(request.form.get('iterations', 100))
    
    # Run tuning process
    result = auto_tune(target_freq, target_q, global_model, global_scaler, max_iterations=iterations)
    
    # Create plots
    optimization_plot = create_optimization_plots(result['history'], target_freq, target_q)
    final_results_plot = create_final_results_plot(
        result['param_descriptions'], 
        [result['resonant_frequency'], result['quality_factor']], 
        target_freq, 
        target_q
    )
    
    return jsonify({
        'status': 'success',
        'message': 'Tuning completed successfully',
        'optimal_params': result['optimal_params'],
        'param_descriptions': result['param_descriptions'],
        'resonant_frequency': result['resonant_frequency'],
        'quality_factor': result['quality_factor'],
        'optimization_plot': optimization_plot,
        'final_results_plot': final_results_plot
    })

if __name__ == '__main__':
    app.run(debug=True)