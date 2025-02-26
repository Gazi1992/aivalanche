import numpy as np
import matplotlib.pyplot as plt
from optimization.visualization import plot_function_2d_3d

class Test_Functions:
    @staticmethod
    def rastrigin(x, y):
        """
        2D Rastrigin function
        Global minimum: f(0,0) = 0
        Search domain: [-5.12, 5.12]
        Highly multimodal with regular spacing of local minima
        """
        return 20 + (x**2 - 10*np.cos(2*np.pi*x)) + (y**2 - 10*np.cos(2*np.pi*y))

    @staticmethod
    def rosenbrock(x, y):
        """
        2D Rosenbrock function (banana function)
        Global minimum: f(1,1) = 0
        Search domain: [-2, 2]
        Has a narrow, parabolic valley
        """
        return (1-x)**2 + 100*(y-x**2)**2

    @staticmethod
    def himmelblau(x, y):
        """
        Himmelblau function (2D)
        Four local minima at:
        f(3.0, 2.0) = 0.0
        f(-2.805118, 3.131312) = 0.0
        f(-3.779310, -3.283186) = 0.0
        f(3.584428, -1.848126) = 0.0
        Search domain: [-5, 5]
        """
        return (x**2 + y - 11)**2 + (x + y**2 - 7)**2

    @staticmethod
    def modified_himmelblau(x, y):
        """
        Modified Himmelblau function (2D) with distinctly different minima values
        Four local minima at approximately:
        f(3.0, 2.0) ≈ 0.0 (global minimum)
        f(-2.805118, 3.131312) ≈ 30.0
        f(-3.779310, -3.283186) ≈ 60.0
        f(3.584428, -1.848126) ≈ 15.0
        Search domain: [-5, 5]
        """
        # Original Himmelblau base
        h = (x**2 + y - 11)**2 + (x + y**2 - 7)**2

        # Multiplicative factors to create different minima values
        # Each factor is designed to primarily affect one region
        factor1 = 1 + 5 * np.exp(-0.2 * ((x + 2.805118)**2 + (y - 3.131312)**2))
        factor2 = 1 + 10 * np.exp(-0.2 * ((x + 3.779310)**2 + (y + 3.283186)**2))
        factor3 = 1 + 15 * np.exp(-0.2 * ((x - 3.584428)**2 + (y + 1.848126)**2))

        return h * (factor1 * factor2 * factor3)

    @staticmethod
    def eggholder(x, y):
        """
        Eggholder function (2D)
        Global minimum: f(512, 404.2319) = -959.6407
        Search domain: [-512, 512]
        Many local minima
        """
        return -(y + 47) * np.sin(np.sqrt(abs(x/2 + y + 47))) - x * np.sin(np.sqrt(abs(x - (y + 47))))

    @staticmethod
    def cross_in_tray(x, y):
        """
        Cross-in-Tray Function (2D)
        Global minima:
        f(±1.3491, ±1.3491) = -2.06261
        Search domain: [-10, 10]
        Multiple global minima
        """
        return -0.0001 * (abs(np.sin(x) * np.sin(y) *
               np.exp(abs(100 - np.sqrt(x**2 + y**2)/np.pi))) + 1)**0.1

    @staticmethod
    def holder_table(x, y):
        """
        Holder Table Function (2D)
        Global minima:
        f(±8.05502, ±9.66459) = -19.2085
        Search domain: [-10, 10]
        Multiple global minima
        """
        return -abs(np.sin(x) * np.cos(y) * np.exp(abs(1 - np.sqrt(x**2 + y**2)/np.pi)))

    @staticmethod
    def schaffer_n2(x, y):
        """
        Schaffer N.2 Function (2D)
        Global minimum: f(0,0) = 0
        Search domain: [-100, 100]
        Highly multimodal
        """
        return 0.5 + (np.sin(x**2 - y**2)**2 - 0.5)/(1 + 0.001*(x**2 + y**2))**2

    @staticmethod
    def levy_n13(x, y):
        """
        Levy N.13 Function (2D)
        Global minimum: f(1,1) = 0
        Search domain: [-10, 10]
        Multiple local minima
        """
        return np.sin(3*np.pi*x)**2 + (x-1)**2*(1 + np.sin(3*np.pi*y)**2) + (y-1)**2*(1 + np.sin(2*np.pi*y)**2)

    @staticmethod
    def three_hump_camel(x, y):
        """
        Three-Hump Camel Function (2D)
        Global minimum: f(0,0) = 0
        Search domain: [-5, 5]
        Has three local minima
        """
        return 2*x**2 - 1.05*x**4 + (x**6)/6 + x*y + y**2

    @staticmethod
    def easom(x, y):
        """
        Easom Function (2D)
        Global minimum: f(π,π) = -1
        Search domain: [-100, 100]
        Needle in a haystack problem
        """
        return -np.cos(x)*np.cos(y)*np.exp(-(x-np.pi)**2 - (y-np.pi)**2)

if __name__ == '__main__':
    # Define functions to plot with their domains and titles
    functions_to_plot = [
        (Test_Functions.himmelblau, (-5, 5), (-5, 5), "Himmelblau Function"),
        (Test_Functions.modified_himmelblau, (-4, 4), (-4, 4), "Modified Himmelblau Function"),
        (Test_Functions.rastrigin, (-5.12, 5.12), (-5.12, 5.12), "Rastrigin Function"),
        (Test_Functions.rosenbrock, (-2, 2), (-2, 2), "Rosenbrock Function"),
        (Test_Functions.cross_in_tray, (-2, 2), (-2, 2), "Cross-in-Tray Function"),
        (Test_Functions.holder_table, (-10, 10), (-10, 10), "Holder Table Function"),
        (Test_Functions.schaffer_n2, (-100, 100), (-100, 100), "Schaffer N.2 Function"),
        (Test_Functions.levy_n13, (-10, 10), (-10, 10), "Levy N.13 Function"),
        (Test_Functions.three_hump_camel, (-5, 5), (-5, 5), "Three-Hump Camel Function"),
        (Test_Functions.easom, (-100, 100), (-100, 100), "Easom Function"),
        (Test_Functions.eggholder, (450, 650), (300, 500), "Eggholder Function")
    ]

    # Create combined plots for each function
    for func, x_range, y_range, title in functions_to_plot:
        fig, (ax1, ax2, ax3) = plot_function_2d_3d(func, x_range, y_range, title)

        # Add known minima where applicable
        if func == Test_Functions.himmelblau:
            minima = [
                (3.0, 2.0),
                (-2.805118, 3.131312),
                (-3.779310, -3.283186),
                (3.584428, -1.848126)
            ]
            for x, y in minima:
                ax2.plot(x, y, 'r*', markersize=10)
                ax3.plot(x, y, 'r*', markersize=10)

        elif func == Test_Functions.cross_in_tray:
            minima = [
                (1.3491, 1.3491),
                (1.3491, -1.3491),
                (-1.3491, 1.3491),
                (-1.3491, -1.3491)
            ]
            for x, y in minima:
                ax2.plot(x, y, 'r*', markersize=10)
                ax3.plot(x, y, 'r*', markersize=10)

        elif func == Test_Functions.holder_table:
            minima = [
                (8.05502, 9.66459),
                (8.05502, -9.66459),
                (-8.05502, 9.66459),
                (-8.05502, -9.66459)
            ]
            for x, y in minima:
                ax2.plot(x, y, 'r*', markersize=10)
                ax3.plot(x, y, 'r*', markersize=10)

        elif func == Test_Functions.easom:
            ax2.plot(np.pi, np.pi, 'r*', markersize=10)
            ax3.plot(np.pi, np.pi, 'r*', markersize=10)

    plt.show()
