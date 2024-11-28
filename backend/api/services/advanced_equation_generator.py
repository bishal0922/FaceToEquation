import numpy as np
from scipy.interpolate import splprep, splev, CubicSpline
from scipy.optimize import curve_fit, minimize
import logging
from typing import List, Dict, Any, Tuple
import math

logger = logging.getLogger(__name__)

class AdvancedEquationGenerator:
    def __init__(self):
        self.feature_handlers = {
            'jawline': self._handle_jawline,
            'right_eyebrow': self._handle_eyebrow,
            'left_eyebrow': self._handle_eyebrow,
            'nose_bridge': self._handle_nose_bridge,
            'nose_tip': self._handle_nose_tip,
            'right_eye': self._handle_eye,
            'left_eye': self._handle_eye,
            'outer_lips': self._handle_outer_lips,
            'inner_lips': self._handle_inner_lips
        }

    def generate(self, feature_name: str, points: List[List[float]]) -> Dict[str, Any]:
        """
        Generate equations for a specific facial feature.
        
        Args:
            feature_name: Name of the facial feature
            points: List of [x, y] coordinates
            
        Returns:
            Dictionary containing equation parameters and type
        """
        try:
            if feature_name not in self.feature_handlers:
                raise ValueError(f"Unknown feature: {feature_name}")

            points = np.array(points)
            return self.feature_handlers[feature_name](points)
        except Exception as e:
            logger.error(f"Error generating equations for {feature_name}: {str(e)}")
            raise

    def _handle_jawline(self, points: np.ndarray) -> Dict[str, Any]:
        """
        Generate a natural cubic spline for the jawline with special handling for the chin area.
        Uses multiple segments to better capture the jawline shape.
        """
        try:
            # Find chin point (lowest y-value)
            chin_idx = np.argmax(points[:, 1])
            
            # Split points into left and right segments
            left_points = points[:chin_idx + 1]
            right_points = points[chin_idx:]
            
            # Generate splines for each segment
            left_spline = self._generate_natural_spline(left_points)
            right_spline = self._generate_natural_spline(right_points)
            
            # Combine into piecewise spline
            return {
                'type': 'piecewise_spline',
                'segments': {
                    'left': left_spline,
                    'right': right_spline
                },
                'chin_point': points[chin_idx].tolist(),
                'bounds': {
                    'x': [float(min(points[:, 0])), float(max(points[:, 0]))],
                    'y': [float(min(points[:, 1])), float(max(points[:, 1]))]
                }
            }
        except Exception as e:
            logger.error(f"Error in jawline handling: {str(e)}")
            raise

    def _handle_eyebrow(self, points: np.ndarray) -> Dict[str, Any]:
        """
        Generate a combination of quadratic Bézier curves for eyebrows,
        capturing the natural arch and thickness.
        """
        try:
            # Sort points by x-coordinate
            sorted_idx = np.argsort(points[:, 0])
            points = points[sorted_idx]
            
            # Find the peak point (highest y-value)
            peak_idx = np.argmin(points[:, 1])
            
            # Split into two segments
            inner_points = points[:peak_idx + 1]
            outer_points = points[peak_idx:]
            
            # Generate Bézier curves for each segment
            inner_curve = self._fit_quadratic_bezier(inner_points)
            outer_curve = self._fit_quadratic_bezier(outer_points)
            
            return {
                'type': 'composite_bezier',
                'segments': {
                    'inner': inner_curve,
                    'outer': outer_curve
                },
                'peak_point': points[peak_idx].tolist(),
                'bounds': {
                    'x': [float(min(points[:, 0])), float(max(points[:, 0]))],
                    'y': [float(min(points[:, 1])), float(max(points[:, 1]))]
                }
            }
        except Exception as e:
            logger.error(f"Error in eyebrow handling: {str(e)}")
            raise

    def _handle_eye(self, points: np.ndarray) -> Dict[str, Any]:
        """
        Generate parametric equations for eyes using ellipse fitting
        with additional parameters for eye corners.
        """
        try:
            # Calculate center
            center = np.mean(points, axis=0)
            
            # Translate points to origin
            centered = points - center
            
            # Fit ellipse parameters
            params = self._fit_ellipse(centered)
            
            # Find eye corners (leftmost and rightmost points)
            corners = points[np.argsort(points[:, 0])[[0, -1]]]
            
            return {
                'type': 'parametric_eye',
                'center': center.tolist(),
                'parameters': {
                    'a': float(params[0]),  # semi-major axis
                    'b': float(params[1]),  # semi-minor axis
                    'theta': float(params[2]),  # rotation angle
                },
                'corners': corners.tolist(),
                'bounds': {
                    'x': [float(min(points[:, 0])), float(max(points[:, 0]))],
                    'y': [float(min(points[:, 1])), float(max(points[:, 1]))]
                }
            }
        except Exception as e:
            logger.error(f"Error in eye handling: {str(e)}")
            raise

    def _handle_nose_bridge(self, points: np.ndarray) -> Dict[str, Any]:
        """
        Generate a smooth curve for the nose bridge using
        a cubic Hermite spline with natural boundary conditions.
        """
        try:
            # Sort points by y-coordinate
            sorted_idx = np.argsort(points[:, 1])
            points = points[sorted_idx]
            
            # Fit cubic Hermite spline
            spline = self._fit_hermite_spline(points)
            
            return {
                'type': 'hermite_spline',
                'control_points': points.tolist(),
                'parameters': spline,
                'bounds': {
                    'x': [float(min(points[:, 0])), float(max(points[:, 0]))],
                    'y': [float(min(points[:, 1])), float(max(points[:, 1]))]
                }
            }
        except Exception as e:
            logger.error(f"Error in nose bridge handling: {str(e)}")
            raise

    def _handle_nose_tip(self, points: np.ndarray) -> Dict[str, Any]:
        """
        Generate equations for nose tip using a combination of
        parabolic curves and line segments.
        """
        try:
            # Find center point
            center_idx = len(points) // 2
            center_point = points[center_idx]
            
            # Fit parabola to points
            parabola_params = self._fit_parabola(points)
            
            return {
                'type': 'nose_tip',
                'center_point': center_point.tolist(),
                'parabola': {
                    'a': float(parabola_params[0]),
                    'b': float(parabola_params[1]),
                    'c': float(parabola_params[2])
                },
                'bounds': {
                    'x': [float(min(points[:, 0])), float(max(points[:, 0]))],
                    'y': [float(min(points[:, 1])), float(max(points[:, 1]))]
                }
            }
        except Exception as e:
            logger.error(f"Error in nose tip handling: {str(e)}")
            raise

    def _handle_outer_lips(self, points: np.ndarray) -> Dict[str, Any]:
        """
        Generate equations for outer lips using composite Bézier curves
        with special handling for the Cupid's bow.
        """
        try:
            # Find lip corners
            corners = points[np.argsort(points[:, 0])[[0, -1]]]
            
            # Split upper and lower lips
            mid = len(points) // 2
            upper_points = points[:mid]
            lower_points = points[mid:]
            
            # Special handling for Cupid's bow
            cupids_bow = self._fit_cupids_bow(upper_points[:5])
            
            # Fit curves for remaining parts
            upper_curve = self._fit_cubic_bezier(upper_points[4:])
            lower_curve = self._fit_cubic_bezier(lower_points)
            
            return {
                'type': 'composite_lips',
                'cupids_bow': cupids_bow,
                'curves': {
                    'upper': upper_curve,
                    'lower': lower_curve
                },
                'corners': corners.tolist(),
                'bounds': {
                    'x': [float(min(points[:, 0])), float(max(points[:, 0]))],
                    'y': [float(min(points[:, 1])), float(max(points[:, 1]))]
                }
            }
        except Exception as e:
            logger.error(f"Error in outer lips handling: {str(e)}")
            raise

    def _handle_inner_lips(self, points: np.ndarray) -> Dict[str, Any]:
        """
        Generate equations for inner lips using simpler Bézier curves.
        """
        try:
            # Split upper and lower
            mid = len(points) // 2
            upper_points = points[:mid]
            lower_points = points[mid:]
            
            # Fit Bézier curves
            upper_curve = self._fit_quadratic_bezier(upper_points)
            lower_curve = self._fit_quadratic_bezier(lower_points)
            
            return {
                'type': 'inner_lips',
                'curves': {
                    'upper': upper_curve,
                    'lower': lower_curve
                },
                'bounds': {
                    'x': [float(min(points[:, 0])), float(max(points[:, 0]))],
                    'y': [float(min(points[:, 1])), float(max(points[:, 1]))]
                }
            }
        except Exception as e:
            logger.error(f"Error in inner lips handling: {str(e)}")
            raise

    def _generate_natural_spline(self, points: np.ndarray) -> Dict[str, Any]:
        """Generate a natural cubic spline."""
        tck, u = splprep([points[:, 0], points[:, 1]], s=0, k=3)
        return {
            'knots': tck[0].tolist(),
            'coefficients': [c.tolist() for c in tck[1]],
            'degree': 3
        }

    def _fit_quadratic_bezier(self, points: np.ndarray) -> Dict[str, Any]:
        """Fit a quadratic Bézier curve to points."""
        n = len(points)
        t = np.linspace(0, 1, n)
        
        # Quadratic Bézier basis
        B = np.array([(1-t)**2, 2*t*(1-t), t**2]).T
        
        # Solve for control points
        px = np.linalg.lstsq(B, points[:, 0], rcond=None)[0]
        py = np.linalg.lstsq(B, points[:, 1], rcond=None)[0]
        
        return {
            'control_points': list(zip(px.tolist(), py.tolist())),
            'degree': 2
        }

    def _fit_cubic_bezier(self, points: np.ndarray) -> Dict[str, Any]:
        """Fit a cubic Bézier curve to points."""
        n = len(points)
        t = np.linspace(0, 1, n)
        
        # Cubic Bézier basis
        B = np.array([(1-t)**3, 3*t*(1-t)**2, 3*t**2*(1-t), t**3]).T
        
        # Solve for control points
        px = np.linalg.lstsq(B, points[:, 0], rcond=None)[0]
        py = np.linalg.lstsq(B, points[:, 1], rcond=None)[0]
        
        return {
            'control_points': list(zip(px.tolist(), py.tolist())),
            'degree': 3
        }

    def _fit_ellipse(self, points: np.ndarray) -> np.ndarray:
        """Fit an ellipse to points using least squares optimization."""
        def ellipse_error(params):
            a, b, theta = params
            x = points[:, 0]
            y = points[:, 1]
            cos_t = np.cos(theta)
            sin_t = np.sin(theta)
            
            x_rot = x * cos_t + y * sin_t
            y_rot = -x * sin_t + y * cos_t
            
            return np.sum((x_rot/a)**2 + (y_rot/b)**2 - 1)**2
        
        # Initial guess
        a0 = np.std(points[:, 0]) * 2
        b0 = np.std(points[:, 1]) * 2
        theta0 = 0
        
        result = minimize(ellipse_error, [a0, b0, theta0], method='Nelder-Mead')
        return result.x

    def _fit_hermite_spline(self, points: np.ndarray) -> Dict[str, Any]:
        """Fit a cubic Hermite spline with natural boundary conditions."""
        x = points[:, 1]  # Use y as parameter
        y = points[:, 0]  # Fit x values
        cs = CubicSpline(x, y, bc_type='natural')
        
        return {
            'c': cs.c.tolist(),
            'x': x.tolist(),
            'degree': 3
        }

    def _fit_parabola(self, points: np.ndarray) -> np.ndarray:
        """Fit a parabola to points."""
        x = points[:, 0]
        y = points[:, 1]
        A = np.vstack([x**2, x, np.ones(len(x))]).T
        return np.linalg.lstsq(A, y, rcond=None)[0]

    def _fit_cupids_bow(self, points: np.ndarray) -> Dict[str, Any]:
        """
        Special fitting for Cupid's bow shape using multiple Bézier curves
        to capture the characteristic M-shape of the upper lip.
        """
        # Find the central peak (Cupid's bow peak)
        mid_idx = len(points) // 2
        peak_point = points[mid_idx]
        
        # Split points into left and right segments
        left_points = points[:mid_idx + 1]
        right_points = points[mid_idx:]
        
        # Find control points for enhanced curvature
        def get_control_points(pts, is_left):
            start = pts[0] if is_left else pts[-1]
            end = pts[-1] if is_left else pts[0]
            
            # Calculate perpendicular vector for control point
            direction = end - start
            length = np.linalg.norm(direction)
            normal = np.array([-direction[1], direction[0]]) / length
            
            # Position control point using perpendicular offset
            control = (start + end) / 2 + normal * (length * 0.25)
            return control
        
        # Generate control points for each segment
        left_control = get_control_points(left_points, True)
        right_control = get_control_points(right_points, False)
        
        return {
            'type': 'cupids_bow',
            'peak_point': peak_point.tolist(),
            'segments': {
                'left': {
                    'start': left_points[0].tolist(),
                    'control': left_control.tolist(),
                    'end': peak_point.tolist()
                },
                'right': {
                    'start': peak_point.tolist(),
                    'control': right_control.tolist(),
                    'end': right_points[-1].tolist()
                }
            },
            'bounds': {
                'x': [float(min(points[:, 0])), float(max(points[:, 0]))],
                'y': [float(min(points[:, 1])), float(max(points[:, 1]))]
            }
        }

    def _evaluate_bezier_curve(self, control_points: List[List[float]], num_points: int = 50) -> np.ndarray:
        """
        Evaluate a Bézier curve given its control points.
        """
        t = np.linspace(0, 1, num_points)
        n = len(control_points) - 1
        points = np.zeros((num_points, 2))
        
        for i, point in enumerate(control_points):
            points += np.outer(
                self._bernstein(n, i, t),
                point
            )
        
        return points

    def _bernstein(self, n: int, i: int, t: np.ndarray) -> np.ndarray:
        """
        Compute Bernstein polynomial basis function.
        """
        return self._binomial(n, i) * (t ** i) * ((1 - t) ** (n - i))

    def _binomial(self, n: int, i: int) -> float:
        """
        Compute binomial coefficient.
        """
        if i < 0 or i > n:
            return 0
        if i == 0 or i == n:
            return 1
        return math.factorial(n) // (math.factorial(i) * math.factorial(n - i))

_generator = AdvancedEquationGenerator()

def get_advanced_generator():
    return _generator