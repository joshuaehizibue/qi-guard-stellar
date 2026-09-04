from setuptools import setup, find_packages

setup(
    name="qi-guard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
    ],
)
