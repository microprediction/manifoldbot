"""
Setup script for ManifoldBot.

ManifoldBot is a comprehensive Python package for creating intelligent trading bots
that interact with Manifold Markets.
"""

from setuptools import find_packages, setup

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="manifoldbot",
    version="0.2.2",
    author="ManifoldBot Contributors",
    author_email="",
    description="A comprehensive Python package for creating intelligent trading bots that interact with Manifold Markets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/petercotton/manifoldbot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
        "dev": [
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "manifoldbot=manifoldbot.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
