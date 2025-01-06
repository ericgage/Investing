from setuptools import setup, find_packages

setup(
    name="etf-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yfinance",
        "pandas",
        "numpy",
        "click",
        "rich",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for analyzing ETF performance and characteristics",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/etf-analyzer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'etf-analyzer=etf_analyzer.cli:cli',
        ],
    },
) 