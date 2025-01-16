from setuptools import setup, find_packages

setup(
    name="etf-analyzer",
    version="0.3.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'yfinance',
        'pandas',
        'numpy',
        'requests',
        'beautifulsoup4',
        'selenium',
        'webdriver_manager',
        'rich'
    ],
    entry_points={
        'console_scripts': [
            'etfa=etf_analyzer.cli:cli',
        ],
    },
    python_requires='>=3.8',
    author="Eric Gage",
    author_email="ericgage@example.com",
    description="A tool for analyzing ETF performance and metrics",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/etf-analyzer",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 