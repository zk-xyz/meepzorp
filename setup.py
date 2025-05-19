"""
Setup configuration for the Meepzorp project.
"""
from setuptools import setup, find_packages

setup(
    name="meepzorp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "pytest-asyncio",
        "fastapi",
        "uvicorn",
        "pydantic",
    ],
) 