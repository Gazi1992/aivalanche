"""
Demo Script: Cars Dataset Analysis
Comprehensive analysis with correlations, distributions, and predictive insights
"""

# Load the cars dataset
df = load_data('Cars Datasets 2025.csv')
print(f"Cars Dataset: {df.shape[0]} cars, {df.shape[1]} features")
print(f"\nColumns: {list(df.columns)}")

# Data overview
print("\n=== Dataset Overview ===")
print(df.head())

# Select numerical columns for analysis
numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print(f"\nNumerical features: {numerical_cols}")

# Missing data check
missing = df.isnull().sum()
if missing.sum() > 0:
    print(f"\n=== Missing Data ===")
    print(missing[missing > 0])

# Statistical summary
print("\n=== Statistical Summary ===")
print(df[numerical_cols].describe())

# Correlation heatmap for numerical features
if len(numerical_cols) > 1:
    corr_matrix = df[numerical_cols].corr()
    
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title='Correlation')
    ))
    
    fig_corr.update_layout(
        title='Feature Correlation Matrix',
        width=800,
        height=700
    )
    register_plot(fig_corr, plot_id='cars_correlation',
                  metadata={'analysis': 'correlation', 'features': len(numerical_cols)})

# Price distribution analysis (if price column exists)
price_cols = [col for col in df.columns if 'price' in col.lower()]
if price_cols:
    price_col = price_cols[0]
    
    # Remove any non-numeric values and convert to float
    df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
    df_price = df.dropna(subset=[price_col])
    
    # Price distribution
    fig_price = make_subplots(rows=1, cols=2,
                             subplot_titles=('Price Distribution', 'Log Price Distribution'))
    
    fig_price.add_trace(go.Histogram(x=df_price[price_col], nbinsx=30,
                                     name='Price', marker_color='lightblue'),
                       row=1, col=1)
    
    # Log scale for better visualization of skewed data
    log_prices = np.log10(df_price[price_col][df_price[price_col] > 0])
    fig_price.add_trace(go.Histogram(x=log_prices, nbinsx=30,
                                     name='Log(Price)', marker_color='lightgreen'),
                       row=1, col=2)
    
    fig_price.update_layout(title='Car Price Analysis', height=400, showlegend=False)
    register_plot(fig_price, plot_id='price_distribution')
    
    # Outlier detection in prices
    price_outliers = find_outliers(df_price, price_col, method='iqr')
    print(f"\n=== Price Outliers ===")
    print(f"Found {len(price_outliers)} cars with unusual prices")
    if len(price_outliers) > 0 and len(price_outliers) < 10:
        print(price_outliers[[price_col]].head())

# Engine size vs MPG analysis (if columns exist)
engine_cols = [col for col in df.columns if 'engine' in col.lower() or 'displacement' in col.lower()]
mpg_cols = [col for col in df.columns if 'mpg' in col.lower() or 'fuel' in col.lower()]

if engine_cols and mpg_cols:
    engine_col = engine_cols[0]
    mpg_col = mpg_cols[0]
    
    # Clean data
    df_clean = df[[engine_col, mpg_col]].dropna()
    df_clean = df_clean[(df_clean[engine_col] > 0) & (df_clean[mpg_col] > 0)]
    
    if len(df_clean) > 0:
        fig_efficiency = px.scatter(df_clean, x=engine_col, y=mpg_col,
                                   title='Engine Size vs Fuel Efficiency',
                                   labels={engine_col: 'Engine Size', mpg_col: 'MPG'},
                                   trendline='ols')
        fig_efficiency.update_traces(marker=dict(size=8, opacity=0.6))
        register_plot(fig_efficiency, plot_id='engine_efficiency',
                     metadata={'analysis': 'regression', 'samples': len(df_clean)})

# Brand analysis (if brand/make column exists)
brand_cols = [col for col in df.columns if 'brand' in col.lower() or 'make' in col.lower()]
if brand_cols:
    brand_col = brand_cols[0]
    brand_counts = df[brand_col].value_counts().head(15)
    
    fig_brands = go.Figure(data=[
        go.Bar(x=brand_counts.index, y=brand_counts.values,
               marker_color='skyblue')
    ])
    fig_brands.update_layout(
        title='Top 15 Car Brands in Dataset',
        xaxis_title='Brand',
        yaxis_title='Count',
        xaxis_tickangle=-45
    )
    register_plot(fig_brands, plot_id='brand_distribution')

# Multi-dimensional analysis using parallel coordinates
# Select 4-6 most interesting numerical features
if len(numerical_cols) >= 4:
    # Try to select diverse features
    selected_features = []
    for keyword in ['price', 'mpg', 'engine', 'year', 'mileage', 'horsepower']:
        for col in numerical_cols:
            if keyword in col.lower() and col not in selected_features:
                selected_features.append(col)
                break
        if len(selected_features) >= 5:
            break
    
    if len(selected_features) >= 3:
        df_parallel = df[selected_features].dropna()
        
        # Normalize values for better visualization
        df_norm = (df_parallel - df_parallel.min()) / (df_parallel.max() - df_parallel.min())
        
        fig_parallel = go.Figure(data=
            go.Parcoords(
                line=dict(color=df_norm.iloc[:, 0],
                         colorscale='Viridis',
                         showscale=True),
                dimensions=[dict(range=[df_parallel[col].min(), df_parallel[col].max()],
                                label=col, values=df_parallel[col])
                           for col in selected_features]
            )
        )
        
        fig_parallel.update_layout(
            title='Multi-dimensional Car Features Analysis',
            height=500
        )
        register_plot(fig_parallel, plot_id='cars_parallel_coords',
                     metadata={'features': selected_features, 'samples': len(df_parallel)})

print(f"\n=== Analysis Summary ===")
print(f"✓ Analyzed {df.shape[0]} cars with {df.shape[1]} features")
print(f"✓ Generated correlation matrix for {len(numerical_cols)} numerical features")
print(f"✓ Created {len(datasets)} visualizations")
print(f"✓ Identified {len(price_outliers) if 'price_outliers' in locals() else 0} price outliers")