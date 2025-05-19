from setuptools import setup, find_packages

setup(
    name="mcp-personal-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "requests",
        "loguru"
    ],
) 