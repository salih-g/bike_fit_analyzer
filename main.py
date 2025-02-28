"""
Entry point for the Bike Fit Analyzer application.
"""
from bike_fit_analyzer.core.analyzer import BikeFitAnalyzer


def main():
    """Main entry point for the application."""
    analyzer = BikeFitAnalyzer()
    analyzer.run(mirror=True)


if __name__ == "__main__":
    main()