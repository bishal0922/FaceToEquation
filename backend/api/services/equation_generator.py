# backend/api/services/equation_generator.py
import numpy as np
from scipy.optimize import curve_fit
from typing import List, Tuple, Dict

class EquationGenerator:
    def __init__(self):
        self.methods = {
            'polynomial': self._fit_polynomial,
            'trigonometric': self._fit_trigonometric
        }

    def generate(self, points: List[Tuple[int, int]], method: str = 'polynomial', degree: int = 4) -> Dict:
        """
        Generate equations that describe the face outline.
        
        Args:
            points: List of (x, y) coordinates
            method: Type of equation to generate ('polynomial' or 'trigonometric')
            degree: Degree of polynomial or number of terms for trigonometric
            
        Returns:
            Dictionary containing equation parameters and type
        """
        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])
        
        # Normalize coordinates
        x_norm = (x - x.min()) / (x.max() - x.min())
        y_norm = (y - y.min()) / (y.max() - y.min())
        
        # Generate equations using specified method
        if method in self.methods:
            return self.methods[method](x_norm, y_norm, degree)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _fit_polynomial(self, x: np.ndarray, y: np.ndarray, degree: int) -> Dict:
        """Fit polynomial equations to the points."""
        coeffs = np.polyfit(x, y, degree)
        
        # Convert coefficients to equation string
        equation = "y = "
        for i, coeff in enumerate(coeffs):
            power = degree - i
            if power > 0:
                equation += f"{coeff:.4f}x^{power} + "
            else:
                equation += f"{coeff:.4f}"
        
        return {
            "type": "polynomial",
            "coefficients": coeffs.tolist(),
            "degree": degree,
            "equation": equation
        }

    def _fit_trigonometric(self, x: np.ndarray, y: np.ndarray, terms: int) -> Dict:
        """Fit trigonometric series to the points."""
        def trig_series(x, *params):
            result = params[0]  # offset
            for i in range(1, len(params), 2):
                if i + 1 < len(params):
                    result += params[i] * np.sin(i * np.pi * x) + params[i+1] * np.cos(i * np.pi * x)
            return result
        
        # Initial parameter guess
        p0 = np.zeros(2 * terms + 1)
        
        # Fit the function
        params, _ = curve_fit(trig_series, x, y, p0=p0)
        
        # Generate equation string
        equation = f"y = {params[0]:.4f}"
        for i in range(1, len(params), 2):
            if i + 1 < len(params):
                equation += f" + {params[i]:.4f}sin({i}πx) + {params[i+1]:.4f}cos({i}πx)"
        
        return {
            "type": "trigonometric",
            "parameters": params.tolist(),
            "terms": terms,
            "equation": equation
        }

equation_generator = EquationGenerator()