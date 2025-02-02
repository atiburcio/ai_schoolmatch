from setuptools import setup, find_packages

setup(
    name="schoolmatch",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langgraph",
        "chromadb",
        "fastapi",
        "uvicorn",
        "openai"
    ],
)
