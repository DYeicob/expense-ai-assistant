from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="expense-ai-assistant",
    version="1.0.0",
    author="Jacobo Montero Naranjo",
    author_email="monteronaranjojacobo@gmail.com",
    description="Intelligent personal expense management system with AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/expense-ai-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.23.3",
            "black>=24.1.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "notebook>=7.0.0",
            "matplotlib>=3.8.2",
            "seaborn>=0.13.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "expense-ai=backend.api.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml"],
    },
    zip_safe=False,
)
