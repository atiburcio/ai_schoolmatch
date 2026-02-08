from setuptools import find_packages, setup

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
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "schoolmatch=langchain_app.cli:main",
        ]
    },
)
