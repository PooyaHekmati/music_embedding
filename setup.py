from distutils.core import setup
from pathlib import Path


def _get_long_description():
    readme_path = Path(__file__).parent / "README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        return f.read()


VERSION = "1.1.2"

setup(
    name="music_embedding",
    packages=["music_embedding"],
    version=VERSION,
    license="MIT",
    description="A package for representing music data based on music theory",
    author="Pooya Hekmati",
    author_email="s.pooyahekmati.a@gmail.com",
    url="https://github.com/PooyaHekmati",
    long_description=_get_long_description(),
    long_description_content_type="text/markdown",
    download_url=f"https://github.com/PooyaHekmati/music_embedding/archive/v{VERSION}.tar.gz",
    project_urls={"Documentation": "https://pooyahekmati.github.io/music_embedding/"},
    keywords=[
        "music",
        "interval",
        "pianoroll",
        "embedding",
        "knowledge representation",
    ],
    install_requires=[
        "numpy",
    ],
    extras_require={
        "test": ["pytest>=6.0", "pytest-cov>=2.0"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",  # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.10",
)
