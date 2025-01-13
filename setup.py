from setuptools import setup, find_packages

setup(
    name="etf_analyzer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'click',
        'rich',
        'yfinance',
        'pandas'
    ],
    entry_points={
        'console_scripts': [
            'etfa=etf_analyzer.cli:cli',
        ],
    }
) 