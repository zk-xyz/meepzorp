from setuptools import setup, find_packages

setup(
    name="creative_director",
    version="0.1.0",
    packages=find_packages(include=["creative_director", "creative_director.*"]),
    install_requires=[
        "pydantic>=2.0.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
    ],
    python_requires=">=3.9",
    test_suite="tests",
) 