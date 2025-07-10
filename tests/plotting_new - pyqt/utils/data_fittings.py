import numpy as np
from typing import Tuple, List, Optional, Dict

# NEW: Try importing SciPy interpolate for spline fittings
try:
    from scipy.interpolate import CubicSpline, PchipInterpolator
    _HAS_SCIPY = True
except ImportError:  # Gracefully degrade if SciPy is unavailable
    _HAS_SCIPY = False

class DataFittings:
    """Utility class providing simple statistical/model fits for histogram data.

    Currently supports:
    1. Normal (Gaussian) distribution fit on raw values.
    2. First-order polynomial (linear) regression on histogram counts vs bin centres.
    3. Second-order polynomial (quadratic) regression on histogram counts vs bin centres.
    """

    @staticmethod
    def _mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean-squared error."""
        return float(np.mean(np.square(y_true - y_pred)))

    # ------------------------------------------------------------------
    # Fit helpers
    # ------------------------------------------------------------------
    @classmethod
    def fit_normal(cls, values: np.ndarray, centres: np.ndarray, counts: np.ndarray, bin_width: float) -> Tuple[np.ndarray, float]:
        """Return predicted counts for a fitted normal distribution and its error (MSE)."""
        mu = float(np.mean(values))
        sigma = float(np.std(values))
        if sigma <= 1e-9:
            # Degenerate – return huge error so it won't be chosen
            return np.zeros_like(counts), float('inf')
        scale_factor = len(values) * bin_width  # area under histogram == number of samples
        y_pred = (1.0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((centres - mu) / sigma) ** 2) * scale_factor
        err = cls._mse(counts, y_pred)
        return y_pred, err

    @classmethod
    def fit_polynomial(cls, degree: int, centres: np.ndarray, counts: np.ndarray) -> Tuple[np.ndarray, float]:
        """Polynomial regression of *degree* on histogram counts. Returns prediction and MSE."""
        if len(centres) <= degree:
            # Not enough points – penalise.
            return np.zeros_like(counts), float('inf')
        coeffs = np.polyfit(centres, counts, degree)
        y_pred = np.polyval(coeffs, centres)
        err = cls._mse(counts, y_pred)
        return y_pred, err

    # ------------------------------------------------------------------
    # New spline-based fits (require SciPy)
    # ------------------------------------------------------------------
    @classmethod
    def fit_cubic_spline(cls, centres: np.ndarray, counts: np.ndarray) -> Tuple[np.ndarray, float]:
        """Cubic spline interpolation of histogram counts. If SciPy unavailable, returns inf error."""
        if not _HAS_SCIPY:
            return np.zeros_like(counts), float('inf')
        if len(centres) < 4:  # Need at least 4 points for cubic spline
            return np.zeros_like(counts), float('inf')
        cs = CubicSpline(centres, counts, bc_type='natural')
        y_pred = cs(centres)
        err = cls._mse(counts, y_pred)
        return y_pred, err

    @classmethod
    def fit_hermite_cubic_spline(cls, centres: np.ndarray, counts: np.ndarray) -> Tuple[np.ndarray, float]:
        """Piecewise cubic Hermite (PCHIP) interpolation. Requires SciPy."""
        if not _HAS_SCIPY:
            return np.zeros_like(counts), float('inf')
        if len(centres) < 2:
            return np.zeros_like(counts), float('inf')
        pchip = PchipInterpolator(centres, counts)
        y_pred = pchip(centres)
        err = cls._mse(counts, y_pred)
        return y_pred, err

    # ------------------------------------------------------------------
    # Helper – compute fit based on requested type
    # ------------------------------------------------------------------
    @classmethod
    def get_fit(cls, fit_type: str, values: List[float], centres: np.ndarray, counts: np.ndarray, bin_width: float) -> Dict[str, np.ndarray]:
        """Return fit result dict for the specified *fit_type*. Raises ValueError if unknown."""
        fit_type_norm = fit_type.lower()
        vals_arr = np.asarray(values, dtype=float)

        if fit_type_norm == 'normal':
            y_pred, _ = cls.fit_normal(vals_arr, centres, counts, bin_width)
        elif fit_type_norm == 'linear':
            y_pred, _ = cls.fit_polynomial(1, centres, counts)
        elif fit_type_norm == 'quadratic':
            y_pred, _ = cls.fit_polynomial(2, centres, counts)
        elif fit_type_norm == 'cubic_spline':
            y_pred, _ = cls.fit_cubic_spline(centres, counts)
        elif fit_type_norm in ('hermite_cubic_spline', 'hermite', 'pchip'):
            y_pred, _ = cls.fit_hermite_cubic_spline(centres, counts)
        else:
            raise ValueError(f"Unsupported fitting type: {fit_type}")

        # Generate smooth curve for plotting
        x_min, x_max = float(np.min(centres)), float(np.max(centres))
        x_fit = np.linspace(x_min, x_max, 200)

        if fit_type_norm == 'normal':
            mu = float(np.mean(vals_arr))
            sigma = float(np.std(vals_arr))
            y_fit = (1.0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_fit - mu) / sigma) ** 2) * len(vals_arr) * bin_width
        elif fit_type_norm in ('linear', 'quadratic'):
            deg = 1 if fit_type_norm == 'linear' else 2
            coeffs = np.polyfit(centres, counts, deg)
            y_fit = np.polyval(coeffs, x_fit)
        elif fit_type_norm == 'cubic_spline':
            if not _HAS_SCIPY:
                raise RuntimeError('SciPy required for cubic spline fitting but not available.')
            cs = CubicSpline(centres, counts, bc_type='natural')
            y_fit = cs(x_fit)
        else:  # hermite_cubic_spline
            if not _HAS_SCIPY:
                raise RuntimeError('SciPy required for hermite cubic spline fitting but not available.')
            pchip = PchipInterpolator(centres, counts)
            y_fit = pchip(x_fit)

        return {
            'type': fit_type_norm,
            'x_fit': x_fit,
            'y_fit': y_fit
        }

    # ------------------------------------------------------------------
    # API – choose best fit
    # ------------------------------------------------------------------
    @classmethod
    def best_fit(cls, values: List[float], centres: np.ndarray, counts: np.ndarray, bin_width: float) -> Dict[str, np.ndarray]:
        """Evaluate all available fits and return dict with keys:
           'type', 'x_fit', 'y_fit'. The 'type' can be one of
           'normal', 'linear', 'quadratic', 'cubic_spline', 'hermite_cubic_spline'.
        """
        vals_arr = np.asarray(values, dtype=float)
        fit_results = {}

        # Collect all fits with their errors
        y_pred_norm, err_norm = cls.fit_normal(vals_arr, centres, counts, bin_width)
        fit_results['normal'] = (y_pred_norm, err_norm)

        y_pred_lin, err_lin = cls.fit_polynomial(1, centres, counts)
        fit_results['linear'] = (y_pred_lin, err_lin)

        y_pred_quad, err_quad = cls.fit_polynomial(2, centres, counts)
        fit_results['quadratic'] = (y_pred_quad, err_quad)

        y_pred_cs, err_cs = cls.fit_cubic_spline(centres, counts)
        fit_results['cubic_spline'] = (y_pred_cs, err_cs)

        y_pred_pchip, err_pchip = cls.fit_hermite_cubic_spline(centres, counts)
        fit_results['hermite_cubic_spline'] = (y_pred_pchip, err_pchip)

        # Choose best (minimum error)
        best_type = min(fit_results.items(), key=lambda kv: kv[1][1])[0]

        # Reuse get_fit to build plotting arrays
        return cls.get_fit(best_type, values, centres, counts, bin_width) 