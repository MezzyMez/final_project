import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

def run_cpi_drivers_analysis(input_file):
    # Load the data
    df = pd.read_csv(input_file)
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])
    df.set_index('REF_DATE', inplace=True)
    df = df.dropna(axis=1, how='all')
    df = df.ffill()
    gas_components = [
        'Gasoline',
        'Fuel oil and other fuels',
        'Natural gas',
        'Fuel, parts and supplies for recreational vehicles',
        'Fuel, parts and supplies for passenger vehicles'
    ]
    df = df.drop(columns=[col for col in df.columns if any(gas in col for gas in gas_components)])
    df_pct_change = df.pct_change().dropna()
    X = df_pct_change.drop('All-items', axis=1)
    y = df_pct_change['All-items']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train_scaled, y_train)
    y_pred = rf.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    print("\nModel Performance Metrics (excluding gas/fuel):")
    print(f"Mean Absolute Error (MAE): {mae:.6f}")
    print(f"Mean Squared Error (MSE): {mse:.6f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.6f}")
    print(f"R-squared Score: {r2:.6f}")
    feature_importances = pd.DataFrame({
        'feature': X.columns,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)
    plt.figure(figsize=(12, 8))
    sns.barplot(data=feature_importances.head(20), x='importance', y='feature')
    plt.title('Top 20 Drivers of All-items CPI Changes (Excluding Gas/Fuel)')
    plt.xlabel('Feature Importance')
    plt.ylabel('CPI Component')
    plt.tight_layout()
    plt.savefig('reports/figures/cpi_drivers_no_gas.png')
    plt.close()
    print("\nTop 20 Drivers of All-items CPI Changes (excluding gas/fuel):")
    print(feature_importances.head(20).round({'importance': 3}))
    top_features = feature_importances.head(20)['feature'].tolist()
    correlation_matrix = df_pct_change[['All-items'] + top_features].corr()
    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='RdYlGn', center=0, fmt='.2f')
    plt.title('Correlation Matrix of Top 20 Drivers with All-items CPI Changes (Excluding Gas/Fuel)')
    plt.tight_layout()
    plt.savefig('reports/figures/cpi_correlation_no_gas.png')
    plt.close()
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.title('Actual vs Predicted CPI Changes (Excluding Gas/Fuel)')
    plt.tight_layout()
    plt.savefig('reports/figures/actual_vs_predicted_no_gas.png')
    plt.close()
    feature_importances['cumulative_importance'] = feature_importances['importance'].cumsum()
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, len(feature_importances) + 1), feature_importances['cumulative_importance'], 'b-')
    plt.axhline(y=0.8, color='r', linestyle='--', label='80% of total importance')
    plt.xlabel('Number of Features')
    plt.ylabel('Cumulative Importance')
    plt.title('Cumulative Feature Importance (Excluding Gas/Fuel)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('reports/figures/cumulative_importance_no_gas.png')
    plt.close()
    n_features_80 = len(feature_importances[feature_importances['cumulative_importance'] <= 0.8])
    print(f"\nNumber of features needed to explain 80% of variance: {n_features_80}")
    print("\nThese features are:")
    print(feature_importances.head(n_features_80)[['feature', 'importance', 'cumulative_importance']].round({'importance': 3, 'cumulative_importance': 3})) 
