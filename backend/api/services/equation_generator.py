import numpy as np
from scipy.optimize import curve_fit
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)

class EquationGenerator:
    def __init__(self):
        """Initialize equation generator with available fitting methods."""
        self.methods = {
            'polynomial': self._fit_polynomial,
            'trigonometric': self._fit_trigonometric,
            'fourier': self._fit_fourier
        }

    def generate(self, points: List[Tuple[float, float]], method: str = 'polynomial', degree: int = 4) -> Dict:
        """
        Generate equations that describe the facial feature curves.
        
        Args:
            points: List of normalized (x, y) coordinates
            method: Type of equation to generate ('polynomial', 'trigonometric', or 'fourier')
            degree: Degree of polynomial or number of terms
            
        Returns:
            Dictionary containing equation parameters and type
            
        Raises:
            ValueError: If method is unknown or fitting fails
        """
        if len(points) < 2:
            raise ValueError("Need at least 2 points to generate equation")
        
        try:
            # Convert points to numpy arrays
            points = np.array(points)
            x = points[:, 0]
            y = points[:, 1]
            
            # Ensure points are sorted by x coordinate
            sort_idx = np.argsort(x)
            x = x[sort_idx]
            y = y[sort_idx]
            
            # Generate equations using specified method
            if method in self.methods:
                return self.methods[method](x, y, degree)
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"Error generating equation: {str(e)}")
            raise ValueError(f"Error generating equation: {str(e)}")

    def _fit_polynomial(self, x: np.ndarray, y: np.ndarray, degree: int) -> Dict:
        """Fit polynomial equations to the points."""
        try:
            coeffs = np.polyfit(x, y, degree)
            
            # Generate equation string
            terms = []
            for i, coeff in enumerate(coeffs):
                power = degree - i
                if abs(coeff) > 1e-10:  # Filter out very small coefficients
                    if power > 1:
                        terms.append(f"{coeff:.4f}x^{power}")
                    elif power == 1:
                        terms.append(f"{coeff:.4f}x")
                    else:
                        terms.append(f"{coeff:.4f}")
            
            equation = "y = " + " + ".join(terms)
            
            return {
                "type": "polynomial",
                "coefficients": coeffs.tolist(),
                "degree": degree,
                "equation": equation
            }
        except Exception as e:
            logger.error(f"Error in polynomial fitting: {str(e)}")
            raise ValueError(f"Error in polynomial fitting: {str(e)}")

    def _fit_trigonometric(self, x: np.ndarray, y: np.ndarray, terms: int) -> Dict:
        """Fit trigonometric series to the points."""
        try:
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
                    if abs(params[i]) > 1e-10:
                        equation += f" + {params[i]:.4f}sin({i}πx)"
                    if abs(params[i+1]) > 1e-10:
                        equation += f" + {params[i+1]:.4f}cos({i}πx)"
            
            return {
                "type": "trigonometric",
                "parameters": params.tolist(),
                "terms": terms,
                "equation": equation
            }
        except Exception as e:
            logger.error(f"Error in trigonometric fitting: {str(e)}")
            raise ValueError(f"Error in trigonometric fitting: {str(e)}")

    def _fit_fourier(self, x: np.ndarray, y: np.ndarray, terms: int) -> Dict:
            """Fit Fourier series to the points."""
            try:
                # Ensure data covers full period
                t = np.linspace(0, 2*np.pi, len(x))
            
                # Calculate Fourier coefficients
                a0 = np.mean(y)
                coeffs_a = []
                coeffs_b = []
            
                for n in range(1, terms + 1):
                    an = np.mean(y * np.cos(n * t)) * 2
                    bn = np.mean(y * np.sin(n * t)) * 2
                    coeffs_a.append(an)
                coeffs_b.append(bn)
            
                # Generate equation string
                equation = f"y = {a0:.4f}"
                for n, (a, b) in enumerate(zip(coeffs_a, coeffs_b), 1):
                    if abs(a) > 1e-10:
                        equation += f" + {a:.4f}cos({n}x)"
                    if abs(b) > 1e-10:
                        equation += f" + {b:.4f}sin({n}x)"
            
                return {
                    "type": "fourier",
                    "a0": a0,
                    "coefficients_a": coeffs_a,
                    "coefficients_b": coeffs_b,
                    "terms": terms,
                    "equation": equation
                }
            except Exception as e:
                logger.error(f"Error in Fourier fitting: {str(e)}")
                raise ValueError(f"Error in Fourier fitting: {str(e)}")

_generator = EquationGenerator()

def get_generator():
    return _generator

# Export these specifically
__all__ = ['get_generator', 'EquationGenerator']