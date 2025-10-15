"""Setup configuration for One Trade package."""
from setuptools import setup, find_packages

with open("README_V2.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(name="one_trade", version="2.0.0", author="", author_email="", description="Modular backtesting and trading system", long_description=long_description, long_description_content_type="text/markdown", url="", packages=find_packages(), classifiers=["Programming Language :: Python :: 3", "Programming Language :: Python :: 3.10", "Programming Language :: Python :: 3.11", "License :: OSI Approved :: MIT License", "Operating System :: OS Independent"], python_requires=">=3.10", install_requires=requirements, entry_points={"console_scripts": ["one-trade=cli.main:cli"]})









