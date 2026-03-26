"""Setup configuration for TFT AutoBot."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tft-autobot",
    version="2.0.0",
    author="TFT AutoBot Contributors",
    description="Automated Teamfight Tactics recommendations and meta learning system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tft-autobot",
    package_dir={"": "src"},
    packages=find_packages("src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "isort>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tft-autobot=cli_main:main",
            "tft-learn=meta_learner:main",
            "tft-scheduler=learner_scheduler:main",
        ],
    },
)
