from pathlib import Path

from setuptools import find_packages, setup


HERE = Path(__file__).resolve().parent


def _read_requirements():
    requirements_path = HERE / "requirements.txt"
    if not requirements_path.exists():
        return []
    return [line.strip() for line in requirements_path.read_text().splitlines() if line.strip()]


def _read_readme():
    readme_path = HERE / "README.md"
    if not readme_path.exists():
        return ""
    return readme_path.read_text(encoding="utf-8")


setup(
    name="printado",
    version="1.0.1",
    description="Ferramenta de captura personalizada",
    long_description=_read_readme(),
    long_description_content_type="text/markdown",
    author="Felipe Haro",
    author_email="felipe@feharo.com.br",
    url="https://github.com/Feharo-Tech/Printado",
    packages=find_packages(),
    install_requires=_read_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "printado=printado.tray:main",
            "printado-capture=printado.main:main",
        ]
    },
    include_package_data=True,
    package_data={
        "printado": [
            "assets/*.png",
        ],
    },
    data_files=[
        ("share/applications", ["desktop/printado.desktop"]),
        ("share/icons/hicolor/256x256/apps", ["printado/assets/printado.png"]),
    ],
)
