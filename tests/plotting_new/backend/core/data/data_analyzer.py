"""
Data Analyzer: Intelligent data analysis and profiling
Analyzes data structure, types, patterns and suggests optimal visualizations
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class DataType(Enum):
    """Data type classifications"""
    NUMERIC_CONTINUOUS = "numeric_continuous"
    NUMERIC_DISCRETE = "numeric_discrete"
    CATEGORICAL = "categorical"
    TEMPORAL = "temporal"
    TEXT = "text"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"

class PlotType(Enum):
    """Available plot types"""
    LINE = "line"
    SCATTER = "scatter"
    BAR = "bar"
    HISTOGRAM = "histogram"
    SCATTER_MATRIX = "scatter_matrix"
    PARALLEL_COORDINATES = "parallel_coordinates"
    HEATMAP = "heatmap"
    BOX = "box"
    VIOLIN = "violin"
    PIE = "pie"
    AREA = "area"

class DataAnalyzer:
    """Analyzes data and suggests optimal visualizations"""
    
    def __init__(self):
        self.analysis_cache = {}
        
    def analyze_dataframe(self, df: pd.DataFrame, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive analysis of a dataframe
        
        Returns:
            Dictionary with analysis results including:
            - column_analysis: Detailed analysis of each column
            - data_patterns: Detected patterns (time series, correlations, etc.)
            - quality_issues: Missing values, outliers, etc.
            - suggested_plots: Recommended visualizations
            - transformations: Suggested data transformations
        """
        logger.info(f"Analyzing dataframe with shape {df.shape}")
        
        analysis = {
            "shape": df.shape,
            "columns": list(df.columns),
            "column_analysis": self._analyze_columns(df),
            "data_patterns": self._detect_patterns(df),
            "quality_issues": self._detect_quality_issues(df),
            "correlations": self._analyze_correlations(df),
            "suggested_plots": [],
            "suggested_transformations": []
        }
        
        # Generate plot suggestions based on analysis
        analysis["suggested_plots"] = self._suggest_plots(analysis)
        
        # Suggest transformations
        analysis["suggested_transformations"] = self._suggest_transformations(analysis)
        
        # Cache the analysis
        if file_path:
            self.analysis_cache[file_path] = analysis
            
        return analysis
    
    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Analyze each column in detail"""
        column_analysis = {}
        
        for col in df.columns:
            col_data = df[col]
            analysis = {
                "name": col,
                "dtype": str(col_data.dtype),
                "data_type": self._classify_column_type(col_data),
                "non_null_count": col_data.notna().sum(),
                "null_count": col_data.isna().sum(),
                "null_percentage": (col_data.isna().sum() / len(df)) * 100,
                "unique_count": col_data.nunique(),
                "unique_percentage": (col_data.nunique() / len(df)) * 100
            }
            
            # Add type-specific analysis
            if analysis["data_type"] in [DataType.NUMERIC_CONTINUOUS, DataType.NUMERIC_DISCRETE]:
                analysis.update(self._analyze_numeric_column(col_data))
            elif analysis["data_type"] == DataType.CATEGORICAL:
                analysis.update(self._analyze_categorical_column(col_data))
            elif analysis["data_type"] == DataType.TEMPORAL:
                analysis.update(self._analyze_temporal_column(col_data))
                
            column_analysis[col] = analysis
            
        return column_analysis
    
    def _classify_column_type(self, series: pd.Series) -> DataType:
        """Classify the data type of a column"""
        # Remove nulls for analysis
        series_clean = series.dropna()
        
        if len(series_clean) == 0:
            return DataType.UNKNOWN
            
        # Check for boolean
        if series.dtype == bool or set(series_clean.unique()) <= {True, False, 0, 1}:
            return DataType.BOOLEAN
            
        # Check for temporal
        if pd.api.types.is_datetime64_any_dtype(series):
            return DataType.TEMPORAL
        
        # Try to parse as datetime
        if series.dtype == object:
            try:
                pd.to_datetime(series_clean.iloc[:100])  # Test first 100 values
                return DataType.TEMPORAL
            except:
                pass
                
        # Check for numeric
        if pd.api.types.is_numeric_dtype(series):
            unique_ratio = series.nunique() / len(series_clean)
            if unique_ratio < 0.05 and series.nunique() < 20:  # Less than 5% unique and < 20 values
                return DataType.CATEGORICAL
            elif series.dtype in ['int64', 'int32', 'int16', 'int8']:
                return DataType.NUMERIC_DISCRETE
            else:
                return DataType.NUMERIC_CONTINUOUS
                
        # Check for categorical/text
        if series.dtype == object:
            avg_length = series_clean.astype(str).str.len().mean()
            unique_ratio = series.nunique() / len(series_clean)
            
            if unique_ratio < 0.5 or series.nunique() < 50:  # Low cardinality
                return DataType.CATEGORICAL
            elif avg_length > 50:  # Long strings
                return DataType.TEXT
            else:
                return DataType.CATEGORICAL
                
        return DataType.UNKNOWN
    
    def _analyze_numeric_column(self, series: pd.Series) -> Dict[str, Any]:
        """Detailed analysis for numeric columns"""
        series_clean = series.dropna()
        
        return {
            "min": float(series_clean.min()),
            "max": float(series_clean.max()),
            "mean": float(series_clean.mean()),
            "median": float(series_clean.median()),
            "std": float(series_clean.std()),
            "q1": float(series_clean.quantile(0.25)),
            "q3": float(series_clean.quantile(0.75)),
            "iqr": float(series_clean.quantile(0.75) - series_clean.quantile(0.25)),
            "skewness": float(series_clean.skew()),
            "kurtosis": float(series_clean.kurtosis()),
            "outliers": self._detect_outliers(series_clean),
            "is_integer": pd.api.types.is_integer_dtype(series) or series_clean.apply(lambda x: x.is_integer() if pd.notna(x) else True).all()
        }
    
    def _analyze_categorical_column(self, series: pd.Series) -> Dict[str, Any]:
        """Detailed analysis for categorical columns"""
        value_counts = series.value_counts()
        
        return {
            "top_values": value_counts.head(10).to_dict(),
            "cardinality": series.nunique(),
            "mode": series.mode()[0] if not series.mode().empty else None,
            "is_ordinal": self._check_if_ordinal(series)
        }
    
    def _analyze_temporal_column(self, series: pd.Series) -> Dict[str, Any]:
        """Detailed analysis for temporal columns"""
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(series):
            try:
                series = pd.to_datetime(series)
            except:
                return {}
                
        series_clean = series.dropna()
        
        return {
            "min_date": series_clean.min().isoformat() if not series_clean.empty else None,
            "max_date": series_clean.max().isoformat() if not series_clean.empty else None,
            "date_range_days": (series_clean.max() - series_clean.min()).days if not series_clean.empty else 0,
            "is_sequential": self._check_if_sequential(series_clean),
            "frequency": self._detect_frequency(series_clean)
        }
    
    def _detect_outliers(self, series: pd.Series) -> Dict[str, Any]:
        """Detect outliers using IQR method"""
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        
        return {
            "count": len(outliers),
            "percentage": (len(outliers) / len(series)) * 100,
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound)
        }
    
    def _check_if_ordinal(self, series: pd.Series) -> bool:
        """Check if categorical column might be ordinal"""
        # Common ordinal patterns
        ordinal_patterns = [
            ['low', 'medium', 'high'],
            ['small', 'medium', 'large'],
            ['poor', 'fair', 'good', 'excellent'],
            ['strongly disagree', 'disagree', 'neutral', 'agree', 'strongly agree']
        ]
        
        values = series.dropna().unique()
        values_lower = [str(v).lower() for v in values]
        
        for pattern in ordinal_patterns:
            if set(values_lower).issubset(set(pattern)):
                return True
                
        return False
    
    def _check_if_sequential(self, series: pd.Series) -> bool:
        """Check if temporal data is sequential"""
        if len(series) < 2:
            return False
            
        sorted_series = series.sort_values()
        diffs = sorted_series.diff().dropna()
        
        # Check if differences are consistent
        return diffs.std() < diffs.mean() * 0.1 if diffs.mean() != 0 else False
    
    def _detect_frequency(self, series: pd.Series) -> Optional[str]:
        """Detect the frequency of temporal data"""
        if len(series) < 2:
            return None
            
        sorted_series = series.sort_values()
        diffs = sorted_series.diff().dropna()
        
        if diffs.empty:
            return None
            
        median_diff = diffs.median()
        
        # Map to common frequencies
        if median_diff.days >= 365:
            return "yearly"
        elif median_diff.days >= 28:
            return "monthly"
        elif median_diff.days >= 7:
            return "weekly"
        elif median_diff.days >= 1:
            return "daily"
        elif median_diff.seconds >= 3600:
            return "hourly"
        else:
            return "high_frequency"
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect patterns in the data"""
        patterns = {
            "has_time_series": False,
            "has_categorical": False,
            "has_geographic": False,
            "has_hierarchical": False,
            "is_wide_format": False,
            "is_long_format": False,
            "potential_pivots": []
        }
        
        # Check for time series
        for col, analysis in self._analyze_columns(df).items():
            if analysis["data_type"] == DataType.TEMPORAL:
                patterns["has_time_series"] = True
                break
                
        # Check for categorical
        categorical_cols = [col for col, analysis in self._analyze_columns(df).items() 
                          if analysis["data_type"] == DataType.CATEGORICAL]
        patterns["has_categorical"] = len(categorical_cols) > 0
        
        # Check data format
        patterns["is_wide_format"] = len(df.columns) > 10 and len(df) < 1000
        patterns["is_long_format"] = len(df.columns) < 5 and len(df) > 1000
        
        # Check for geographic patterns (simple heuristic)
        geo_keywords = ['lat', 'lon', 'latitude', 'longitude', 'country', 'state', 'city', 'region']
        col_names_lower = [col.lower() for col in df.columns]
        patterns["has_geographic"] = any(keyword in ' '.join(col_names_lower) for keyword in geo_keywords)
        
        return patterns
    
    def _detect_quality_issues(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect data quality issues"""
        issues = {
            "missing_values": {},
            "duplicates": {},
            "inconsistencies": [],
            "warnings": []
        }
        
        # Missing values analysis
        missing_by_column = df.isnull().sum()
        if missing_by_column.any():
            issues["missing_values"] = {
                "total": int(df.isnull().sum().sum()),
                "by_column": missing_by_column[missing_by_column > 0].to_dict(),
                "percentage": float((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100)
            }
            
        # Duplicate analysis
        duplicates = df.duplicated()
        if duplicates.any():
            issues["duplicates"] = {
                "count": int(duplicates.sum()),
                "percentage": float((duplicates.sum() / len(df)) * 100)
            }
            
        # Check for inconsistencies
        for col in df.columns:
            # Check for mixed types
            if df[col].dtype == object:
                types = df[col].dropna().apply(type).unique()
                if len(types) > 1:
                    issues["inconsistencies"].append({
                        "column": col,
                        "issue": "mixed_types",
                        "types": [t.__name__ for t in types]
                    })
                    
        # Generate warnings
        if issues["missing_values"] and issues["missing_values"]["percentage"] > 20:
            issues["warnings"].append("High percentage of missing values detected")
            
        if issues["duplicates"] and issues["duplicates"]["percentage"] > 10:
            issues["warnings"].append("Significant number of duplicate rows detected")
            
        return issues
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {"has_correlations": False}
            
        corr_matrix = df[numeric_cols].corr()
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # Strong correlation threshold
                    strong_correlations.append({
                        "column1": corr_matrix.columns[i],
                        "column2": corr_matrix.columns[j],
                        "correlation": float(corr_value)
                    })
                    
        return {
            "has_correlations": len(strong_correlations) > 0,
            "strong_correlations": strong_correlations,
            "numeric_columns": list(numeric_cols)
        }
    
    def _suggest_plots(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest optimal plot types based on data analysis"""
        suggestions = []
        col_analysis = analysis["column_analysis"]
        patterns = analysis["data_patterns"]
        correlations = analysis["correlations"]
        
        # Count column types
        numeric_cols = [col for col, info in col_analysis.items() 
                       if info["data_type"] in [DataType.NUMERIC_CONTINUOUS, DataType.NUMERIC_DISCRETE]]
        categorical_cols = [col for col, info in col_analysis.items() 
                          if info["data_type"] == DataType.CATEGORICAL]
        temporal_cols = [col for col, info in col_analysis.items() 
                        if info["data_type"] == DataType.TEMPORAL]
        
        # Time series plot
        if temporal_cols and numeric_cols:
            suggestions.append({
                "plot_type": PlotType.LINE.value,
                "priority": 1,
                "reason": "Time series data detected",
                "config": {
                    "x_column": temporal_cols[0],
                    "y_columns": numeric_cols[:3],  # Limit to 3 for clarity
                    "title": "Time Series Analysis"
                }
            })
        
        # Scatter plot for correlations
        if correlations["has_correlations"] and correlations["strong_correlations"]:
            for corr in correlations["strong_correlations"][:2]:  # Top 2 correlations
                suggestions.append({
                    "plot_type": PlotType.SCATTER.value,
                    "priority": 2,
                    "reason": f"Strong correlation detected (r={corr['correlation']:.2f})",
                    "config": {
                        "x_column": corr["column1"],
                        "y_column": corr["column2"],
                        "title": f"{corr['column1']} vs {corr['column2']}"
                    }
                })
        
        # Bar chart for categorical data
        if categorical_cols and numeric_cols:
            suggestions.append({
                "plot_type": PlotType.BAR.value,
                "priority": 2,
                "reason": "Categorical and numeric data combination",
                "config": {
                    "x_column": categorical_cols[0],
                    "y_column": numeric_cols[0],
                    "aggregation": "mean",
                    "title": f"{numeric_cols[0]} by {categorical_cols[0]}"
                }
            })
        
        # Histogram for distributions
        for col in numeric_cols[:3]:  # Limit to 3 histograms
            col_info = col_analysis[col]
            if col_info.get("skewness", 0) != 0:  # Interesting distribution
                suggestions.append({
                    "plot_type": PlotType.HISTOGRAM.value,
                    "priority": 3,
                    "reason": f"Analyze distribution (skewness={col_info.get('skewness', 0):.2f})",
                    "config": {
                        "column": col,
                        "bins": 30,
                        "title": f"Distribution of {col}"
                    }
                })
        
        # Scatter matrix for multiple numeric columns
        if len(numeric_cols) >= 3:
            suggestions.append({
                "plot_type": PlotType.SCATTER_MATRIX.value,
                "priority": 3,
                "reason": "Multiple numeric columns for correlation analysis",
                "config": {
                    "columns": numeric_cols[:5],  # Limit to 5 for readability
                    "title": "Scatter Matrix Analysis"
                }
            })
        
        # Parallel coordinates for high-dimensional data
        if len(numeric_cols) >= 4:
            suggestions.append({
                "plot_type": PlotType.PARALLEL_COORDINATES.value,
                "priority": 4,
                "reason": "High-dimensional data visualization",
                "config": {
                    "columns": numeric_cols[:7],  # Limit to 7 dimensions
                    "color_column": categorical_cols[0] if categorical_cols else None,
                    "title": "Parallel Coordinates Plot"
                }
            })
        
        # Sort by priority
        suggestions.sort(key=lambda x: x["priority"])
        
        return suggestions
    
    def _suggest_transformations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest data transformations based on analysis"""
        transformations = []
        col_analysis = analysis["column_analysis"]
        quality_issues = analysis["quality_issues"]
        
        # Handle missing values
        if quality_issues["missing_values"]:
            for col, missing_count in quality_issues["missing_values"].get("by_column", {}).items():
                col_info = col_analysis[col]
                if col_info["data_type"] in [DataType.NUMERIC_CONTINUOUS, DataType.NUMERIC_DISCRETE]:
                    transformations.append({
                        "type": "fill_missing",
                        "column": col,
                        "method": "median",
                        "reason": f"Fill {missing_count} missing values with median"
                    })
                elif col_info["data_type"] == DataType.CATEGORICAL:
                    transformations.append({
                        "type": "fill_missing",
                        "column": col,
                        "method": "mode",
                        "reason": f"Fill {missing_count} missing values with mode"
                    })
        
        # Handle outliers
        for col, info in col_analysis.items():
            if info["data_type"] in [DataType.NUMERIC_CONTINUOUS, DataType.NUMERIC_DISCRETE]:
                outliers = info.get("outliers", {})
                if outliers.get("percentage", 0) > 5:
                    transformations.append({
                        "type": "handle_outliers",
                        "column": col,
                        "method": "clip",
                        "reason": f"Clip {outliers['count']} outliers ({outliers['percentage']:.1f}%)"
                    })
        
        # Suggest computed columns
        if "strong_correlations" in analysis["correlations"]:
            # Don't suggest ratios for highly correlated columns
            pass
        else:
            numeric_cols = [col for col, info in col_analysis.items() 
                          if info["data_type"] in [DataType.NUMERIC_CONTINUOUS, DataType.NUMERIC_DISCRETE]]
            
            # Suggest ratios for certain column name patterns
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i+1:]:
                    if self._should_compute_ratio(col1, col2):
                        transformations.append({
                            "type": "compute_column",
                            "name": f"{col1}_per_{col2}",
                            "formula": f"{col1} / {col2}",
                            "reason": f"Compute ratio of {col1} to {col2}"
                        })
        
        # Suggest datetime extraction
        temporal_cols = [col for col, info in col_analysis.items() 
                        if info["data_type"] == DataType.TEMPORAL]
        
        for col in temporal_cols:
            transformations.extend([
                {
                    "type": "extract_datetime",
                    "column": col,
                    "extract": "year",
                    "new_column": f"{col}_year",
                    "reason": "Extract year for temporal analysis"
                },
                {
                    "type": "extract_datetime",
                    "column": col,
                    "extract": "month",
                    "new_column": f"{col}_month",
                    "reason": "Extract month for seasonal analysis"
                },
                {
                    "type": "extract_datetime",
                    "column": col,
                    "extract": "dayofweek",
                    "new_column": f"{col}_dayofweek",
                    "reason": "Extract day of week for pattern analysis"
                }
            ])
        
        return transformations
    
    def _should_compute_ratio(self, col1: str, col2: str) -> bool:
        """Determine if a ratio between two columns makes sense"""
        # Common patterns where ratios make sense
        ratio_patterns = [
            ("revenue", "cost"),
            ("profit", "revenue"),
            ("sales", "visits"),
            ("conversions", "clicks"),
            ("distance", "time"),
            ("voltage", "current"),  # Resistance
            ("power", "voltage"),   # Current
        ]
        
        col1_lower = col1.lower()
        col2_lower = col2.lower()
        
        for pattern in ratio_patterns:
            if (pattern[0] in col1_lower and pattern[1] in col2_lower) or \
               (pattern[1] in col1_lower and pattern[0] in col2_lower):
                return True
                
        return False
    
    def suggest_plot_from_columns(self, columns: List[str], column_types: Dict[str, DataType]) -> Dict[str, Any]:
        """Suggest a plot type based on selected columns"""
        num_numeric = sum(1 for col in columns if column_types.get(col) in 
                         [DataType.NUMERIC_CONTINUOUS, DataType.NUMERIC_DISCRETE])
        num_categorical = sum(1 for col in columns if column_types.get(col) == DataType.CATEGORICAL)
        num_temporal = sum(1 for col in columns if column_types.get(col) == DataType.TEMPORAL)
        
        # Decision tree for plot selection
        if len(columns) == 1:
            if column_types.get(columns[0]) in [DataType.NUMERIC_CONTINUOUS, DataType.NUMERIC_DISCRETE]:
                return {"plot_type": PlotType.HISTOGRAM.value, "reason": "Single numeric column"}
            elif column_types.get(columns[0]) == DataType.CATEGORICAL:
                return {"plot_type": PlotType.BAR.value, "reason": "Single categorical column"}
                
        elif len(columns) == 2:
            if num_numeric == 2:
                return {"plot_type": PlotType.SCATTER.value, "reason": "Two numeric columns"}
            elif num_numeric == 1 and num_categorical == 1:
                return {"plot_type": PlotType.BAR.value, "reason": "Categorical vs numeric"}
            elif num_numeric == 1 and num_temporal == 1:
                return {"plot_type": PlotType.LINE.value, "reason": "Time series data"}
                
        elif len(columns) >= 3:
            if num_numeric >= 3:
                return {"plot_type": PlotType.SCATTER_MATRIX.value, "reason": "Multiple numeric columns"}
            elif num_temporal == 1 and num_numeric >= 1:
                return {"plot_type": PlotType.LINE.value, "reason": "Multiple time series"}
                
        # Default
        return {"plot_type": PlotType.SCATTER.value, "reason": "Default visualization"}