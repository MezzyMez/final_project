from inflation_predictor import InflationPredictor
import pandas as pd
import matplotlib.pyplot as plt
import os

def main():
    # Initialize the predictor
    predictor = InflationPredictor('data/processed/cpi_processed.csv')
    
    # Print model performance metrics
    print("\nModel Performance Metrics:")
    print(f"Mean Absolute Error (MAE): {predictor.metrics['mae']:.6f}")
    print(f"Mean Squared Error (MSE): {predictor.metrics['mse']:.6f}")
    print(f"Root Mean Squared Error (RMSE): {predictor.metrics['rmse']:.6f}")
    print(f"R-squared Score: {predictor.metrics['r2']:.6f}")
    
    # Get and display feature importance
    importance_df = predictor.get_feature_importance()
    print("\nTop 10 Most Important Product Groups:")
    print(importance_df.head(10))
    
    # Create a bar plot of feature importance
    plt.figure(figsize=(12, 6))
    plt.barh(importance_df['Feature'].head(10), importance_df['Importance'].head(10))
    plt.xlabel('Feature Importance')
    plt.title('Top 10 Most Important Product Groups for Inflation Prediction')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    # Save the plot
    os.makedirs('reports/figures', exist_ok=True)
    plt.savefig('reports/figures/feature_importance.png')
    plt.close()
    
    # Example: Correlated prediction for a 5% increase in Housing
    print("\nCorrelated Prediction Example:")
    user_change = {'Housing (1986 definition)': 0.05}
    correlated_changes = predictor.get_correlated_changes(user_change)
    print("Correlated changes vector (top 10 shown):")
    for k, v in list(correlated_changes.items())[:10]:
        print(f"  {k}: {v:.4f}")
    inflation_impact = predictor.predict_inflation_impact(correlated_changes)
    print(f"\nPredicted overall inflation impact (with correlated changes): {inflation_impact:.4%}")
    
    # Save the model
    predictor.save_model()

if __name__ == "__main__":
    main() 