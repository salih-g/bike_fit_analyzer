from setuptools import setup, find_packages

setup(
    name="bike_fit_analyzer",
    version="1.0.0",
    description="Bicycle fit analysis and guidance using computer vision",
    author="Bike Fit Team",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.5.0",
        "mediapipe>=0.8.10",
        "numpy>=1.20.0",
        "PyQt5>=5.15.0",
    ],
    entry_points={
        "console_scripts": [
            "bike-fit-analyzer=bike_fit_analyzer.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)