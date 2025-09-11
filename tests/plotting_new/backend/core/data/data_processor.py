"""
Data Processor: Intelligent data transformation engine
Handles data cleaning, transformation, and computation using Python expressions
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import logging
import ast
import operator
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class DataProcessor:
    """Process and transform data using Python expressions"""
    
    # Safe operations for eval
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.LShift: operator.lshift,
        ast.RShift: operator.rshift,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        ast.BitAnd: operator.and_,
        ast.FloorDiv: operator.floordiv,
        ast.And: operator.and_,
        ast.Or: operator.or_,
        ast.Not: operator.not_,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
    }
    
    # Safe functions for eval
    SAFE_FUNCTIONS = {
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'len': len,
        'sqrt': np.sqrt,
        'log': np.log,
        'log10': np.log10,
        'exp': np.exp,
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'mean': np.mean,
        'median': np.median,
        'std': np.std,
        'var': np.var,
    }
    
    def __init__(self):
        self.transformation_history = []
        
    def apply_transformations(self, df: pd.DataFrame, transformations: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Apply a series of transformations to a dataframe
        
        Args:
            df: Input dataframe
            transformations: List of transformation specifications
            
        Returns:
            Transformed dataframe
        """
        df_transformed = df.copy()
        
        for i, transform in enumerate(transformations):
            try:
                logger.info(f"Applying transformation {i+1}/{len(transformations)}: {transform.get('type')}")
                df_transformed = self._apply_single_transformation(df_transformed, transform)
                
                # Record successful transformation
                self.transformation_history.append({
                    "index": i,
                    "transformation": transform,
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Failed to apply transformation: {e}")
                self.transformation_history.append({
                    "index": i,
                    "transformation": transform,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                # Continue with other transformations
                
        return df_transformed
    
    def _apply_single_transformation(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Apply a single transformation"""
        transform_type = transform.get("type")
        
        if transform_type == "compute_column":
            return self._compute_column(df, transform)
        elif transform_type == "filter":
            return self._filter_data(df, transform)
        elif transform_type == "aggregate":
            return self._aggregate_data(df, transform)
        elif transform_type == "fill_missing":
            return self._fill_missing(df, transform)
        elif transform_type == "handle_outliers":
            return self._handle_outliers(df, transform)
        elif transform_type == "extract_datetime":
            return self._extract_datetime(df, transform)
        elif transform_type == "pivot":
            return self._pivot_data(df, transform)
        elif transform_type == "melt":
            return self._melt_data(df, transform)
        elif transform_type == "rename_column":
            return self._rename_column(df, transform)
        elif transform_type == "drop_column":
            return self._drop_column(df, transform)
        elif transform_type == "sort":
            return self._sort_data(df, transform)
        elif transform_type == "resample":
            return self._resample_time_series(df, transform)
        else:
            logger.warning(f"Unknown transformation type: {transform_type}")
            return df
    
    def _compute_column(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Compute a new column using a Python expression"""
        column_name = transform.get("name", "computed_column")
        formula = transform.get("formula", "")
        
        if not formula:
            raise ValueError("Formula is required for compute_column transformation")
        
        # Parse and evaluate the formula safely
        try:
            # Replace column references with df['column'] format
            parsed_formula = self._parse_formula(formula, df.columns)
            
            # Create a safe evaluation context
            safe_dict = {
                'df': df,
                'np': np,
                'pd': pd,
                **self.SAFE_FUNCTIONS
            }
            
            # Evaluate the formula
            df[column_name] = eval(parsed_formula, {"__builtins__": {}}, safe_dict)
            logger.info(f"Computed column '{column_name}' using formula: {formula}")
            
        except Exception as e:
            raise ValueError(f"Failed to compute column '{column_name}': {e}")
            
        return df
    
    def _parse_formula(self, formula: str, columns: List[str]) -> str:
        """Parse formula and replace column names with df['column'] format"""
        parsed = formula
        
        # Sort columns by length (longest first) to avoid partial replacements
        sorted_columns = sorted(columns, key=len, reverse=True)
        
        for col in sorted_columns:
            # Use word boundaries to match whole column names
            pattern = r'\b' + re.escape(col) + r'\b'
            replacement = f"df['{col}']"
            parsed = re.sub(pattern, replacement, parsed)
            
        return parsed
    
    def _filter_data(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Filter data based on a condition"""
        condition = transform.get("condition", "")
        
        if not condition:
            raise ValueError("Condition is required for filter transformation")
        
        try:
            # Parse condition
            parsed_condition = self._parse_formula(condition, df.columns)
            
            # Create safe evaluation context
            safe_dict = {
                'df': df,
                'np': np,
                'pd': pd,
                **self.SAFE_FUNCTIONS
            }
            
            # Evaluate condition
            mask = eval(parsed_condition, {"__builtins__": {}}, safe_dict)
            filtered_df = df[mask]
            
            logger.info(f"Filtered data: {len(filtered_df)} rows remaining (from {len(df)})")
            return filtered_df
            
        except Exception as e:
            raise ValueError(f"Failed to filter data: {e}")
    
    def _aggregate_data(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Aggregate data by grouping"""
        group_by = transform.get("group_by", [])
        aggregations = transform.get("aggregations", {})
        
        if not group_by:
            raise ValueError("group_by is required for aggregate transformation")
        
        if isinstance(group_by, str):
            group_by = [group_by]
        
        try:
            # Build aggregation dictionary
            agg_dict = {}
            for col, operations in aggregations.items():
                if isinstance(operations, str):
                    operations = [operations]
                agg_dict[col] = operations
            
            # Perform aggregation
            if agg_dict:
                aggregated = df.groupby(group_by).agg(agg_dict)
                # Flatten column names
                aggregated.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col 
                                     for col in aggregated.columns]
            else:
                # Default to mean for numeric columns
                aggregated = df.groupby(group_by).mean()
            
            aggregated = aggregated.reset_index()
            logger.info(f"Aggregated data by {group_by}: {len(aggregated)} groups")
            
            return aggregated
            
        except Exception as e:
            raise ValueError(f"Failed to aggregate data: {e}")
    
    def _fill_missing(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Fill missing values"""
        column = transform.get("column")
        method = transform.get("method", "forward")
        value = transform.get("value")
        
        try:
            if column:
                # Fill specific column
                if method == "forward":
                    df[column] = df[column].fillna(method='ffill')
                elif method == "backward":
                    df[column] = df[column].fillna(method='bfill')
                elif method == "mean":
                    df[column] = df[column].fillna(df[column].mean())
                elif method == "median":
                    df[column] = df[column].fillna(df[column].median())
                elif method == "mode":
                    mode_value = df[column].mode()[0] if not df[column].mode().empty else None
                    if mode_value is not None:
                        df[column] = df[column].fillna(mode_value)
                elif method == "value" and value is not None:
                    df[column] = df[column].fillna(value)
                elif method == "interpolate":
                    df[column] = df[column].interpolate()
                    
                logger.info(f"Filled missing values in column '{column}' using method '{method}'")
            else:
                # Fill all columns
                if method == "forward":
                    df = df.fillna(method='ffill')
                elif method == "backward":
                    df = df.fillna(method='bfill')
                elif value is not None:
                    df = df.fillna(value)
                    
                logger.info(f"Filled missing values in all columns using method '{method}'")
                
        except Exception as e:
            raise ValueError(f"Failed to fill missing values: {e}")
            
        return df
    
    def _handle_outliers(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Handle outliers in numeric columns"""
        column = transform.get("column")
        method = transform.get("method", "clip")
        threshold = transform.get("threshold", 1.5)  # IQR multiplier
        
        if not column:
            raise ValueError("Column is required for handle_outliers transformation")
        
        try:
            if method == "clip":
                # Clip outliers to bounds
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
                logger.info(f"Clipped outliers in '{column}' to [{lower_bound:.2f}, {upper_bound:.2f}]")
                
            elif method == "remove":
                # Remove outlier rows
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                initial_len = len(df)
                df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
                logger.info(f"Removed {initial_len - len(df)} outlier rows from '{column}'")
                
            elif method == "null":
                # Replace outliers with null
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                df.loc[(df[column] < lower_bound) | (df[column] > upper_bound), column] = np.nan
                logger.info(f"Replaced outliers in '{column}' with null values")
                
        except Exception as e:
            raise ValueError(f"Failed to handle outliers: {e}")
            
        return df
    
    def _extract_datetime(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Extract datetime components"""
        column = transform.get("column")
        extract = transform.get("extract", "year")
        new_column = transform.get("new_column")
        
        if not column:
            raise ValueError("Column is required for extract_datetime transformation")
        
        if not new_column:
            new_column = f"{column}_{extract}"
        
        try:
            # Convert to datetime if needed
            if not pd.api.types.is_datetime64_any_dtype(df[column]):
                df[column] = pd.to_datetime(df[column])
            
            # Extract component
            if extract == "year":
                df[new_column] = df[column].dt.year
            elif extract == "month":
                df[new_column] = df[column].dt.month
            elif extract == "day":
                df[new_column] = df[column].dt.day
            elif extract == "hour":
                df[new_column] = df[column].dt.hour
            elif extract == "minute":
                df[new_column] = df[column].dt.minute
            elif extract == "second":
                df[new_column] = df[column].dt.second
            elif extract == "dayofweek":
                df[new_column] = df[column].dt.dayofweek
            elif extract == "dayofyear":
                df[new_column] = df[column].dt.dayofyear
            elif extract == "weekofyear":
                df[new_column] = df[column].dt.isocalendar().week
            elif extract == "quarter":
                df[new_column] = df[column].dt.quarter
            elif extract == "date":
                df[new_column] = df[column].dt.date
            elif extract == "time":
                df[new_column] = df[column].dt.time
                
            logger.info(f"Extracted {extract} from '{column}' to '{new_column}'")
            
        except Exception as e:
            raise ValueError(f"Failed to extract datetime: {e}")
            
        return df
    
    def _pivot_data(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Pivot data from long to wide format"""
        index = transform.get("index")
        columns = transform.get("columns")
        values = transform.get("values")
        aggfunc = transform.get("aggfunc", "mean")
        
        try:
            pivoted = pd.pivot_table(
                df,
                index=index,
                columns=columns,
                values=values,
                aggfunc=aggfunc,
                fill_value=0
            )
            
            # Flatten column names if multi-level
            if isinstance(pivoted.columns, pd.MultiIndex):
                pivoted.columns = ['_'.join(map(str, col)).strip() for col in pivoted.columns]
            
            pivoted = pivoted.reset_index()
            logger.info(f"Pivoted data: {pivoted.shape}")
            
            return pivoted
            
        except Exception as e:
            raise ValueError(f"Failed to pivot data: {e}")
    
    def _melt_data(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Melt data from wide to long format"""
        id_vars = transform.get("id_vars", [])
        value_vars = transform.get("value_vars")
        var_name = transform.get("var_name", "variable")
        value_name = transform.get("value_name", "value")
        
        try:
            melted = pd.melt(
                df,
                id_vars=id_vars,
                value_vars=value_vars,
                var_name=var_name,
                value_name=value_name
            )
            
            logger.info(f"Melted data: {melted.shape}")
            return melted
            
        except Exception as e:
            raise ValueError(f"Failed to melt data: {e}")
    
    def _rename_column(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Rename columns"""
        old_name = transform.get("old_name")
        new_name = transform.get("new_name")
        mapping = transform.get("mapping", {})
        
        try:
            if old_name and new_name:
                df = df.rename(columns={old_name: new_name})
                logger.info(f"Renamed column '{old_name}' to '{new_name}'")
            elif mapping:
                df = df.rename(columns=mapping)
                logger.info(f"Renamed {len(mapping)} columns")
                
        except Exception as e:
            raise ValueError(f"Failed to rename columns: {e}")
            
        return df
    
    def _drop_column(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Drop columns"""
        columns = transform.get("columns", [])
        
        if isinstance(columns, str):
            columns = [columns]
        
        try:
            df = df.drop(columns=columns)
            logger.info(f"Dropped columns: {columns}")
            
        except Exception as e:
            raise ValueError(f"Failed to drop columns: {e}")
            
        return df
    
    def _sort_data(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Sort data"""
        by = transform.get("by", [])
        ascending = transform.get("ascending", True)
        
        if isinstance(by, str):
            by = [by]
        
        try:
            df = df.sort_values(by=by, ascending=ascending)
            logger.info(f"Sorted data by {by}")
            
        except Exception as e:
            raise ValueError(f"Failed to sort data: {e}")
            
        return df
    
    def _resample_time_series(self, df: pd.DataFrame, transform: Dict[str, Any]) -> pd.DataFrame:
        """Resample time series data"""
        datetime_column = transform.get("datetime_column")
        frequency = transform.get("frequency", "D")  # Daily by default
        aggregation = transform.get("aggregation", "mean")
        
        if not datetime_column:
            raise ValueError("datetime_column is required for resample transformation")
        
        try:
            # Set datetime column as index
            df[datetime_column] = pd.to_datetime(df[datetime_column])
            df = df.set_index(datetime_column)
            
            # Resample
            if aggregation == "mean":
                resampled = df.resample(frequency).mean()
            elif aggregation == "sum":
                resampled = df.resample(frequency).sum()
            elif aggregation == "min":
                resampled = df.resample(frequency).min()
            elif aggregation == "max":
                resampled = df.resample(frequency).max()
            elif aggregation == "count":
                resampled = df.resample(frequency).count()
            elif aggregation == "first":
                resampled = df.resample(frequency).first()
            elif aggregation == "last":
                resampled = df.resample(frequency).last()
            else:
                resampled = df.resample(frequency).mean()
            
            resampled = resampled.reset_index()
            logger.info(f"Resampled time series to {frequency} frequency using {aggregation}")
            
            return resampled
            
        except Exception as e:
            raise ValueError(f"Failed to resample time series: {e}")
    
    def validate_transformation(self, transform: Dict[str, Any], df_columns: List[str]) -> Dict[str, Any]:
        """Validate a transformation before applying"""
        result = {"valid": True, "errors": [], "warnings": []}
        transform_type = transform.get("type")
        
        if not transform_type:
            result["valid"] = False
            result["errors"].append("Transformation type is required")
            return result
        
        # Type-specific validation
        if transform_type == "compute_column":
            if not transform.get("formula"):
                result["errors"].append("Formula is required for compute_column")
                result["valid"] = False
            if not transform.get("name"):
                result["warnings"].append("Column name not specified, using 'computed_column'")
                
        elif transform_type == "filter":
            if not transform.get("condition"):
                result["errors"].append("Condition is required for filter")
                result["valid"] = False
                
        elif transform_type == "aggregate":
            if not transform.get("group_by"):
                result["errors"].append("group_by is required for aggregate")
                result["valid"] = False
                
        # Check if referenced columns exist
        for key in ["column", "columns", "group_by", "index", "id_vars"]:
            if key in transform:
                cols = transform[key]
                if isinstance(cols, str):
                    cols = [cols]
                elif not isinstance(cols, list):
                    continue
                    
                for col in cols:
                    if col not in df_columns:
                        result["errors"].append(f"Column '{col}' not found in dataframe")
                        result["valid"] = False
        
        return result
    
    def get_transformation_history(self) -> List[Dict[str, Any]]:
        """Get the history of applied transformations"""
        return self.transformation_history
    
    def clear_history(self):
        """Clear transformation history"""
        self.transformation_history = []