from setuptools import setup, find_packages

setup(
    name="etf-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'selenium',
        'selenium-stealth',
        'pandas',
        'yfinance',
        'rich',
        'click',
        'pytz',
        'beautifulsoup4',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'etfa=etf_analyzer.cli:cli',
        ],
    },
) 