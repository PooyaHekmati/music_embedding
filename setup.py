from distutils.core import setup
from pathlib import Path

def _get_long_description():
    with open(str(Path(__file__).parent / "README.md"), "r") as f:
        return f.read()

def _get_version():
    with open(str(Path(__file__).parent / "music_embedding/version.py"), "r") as f:
        for line in f:
            if line.startswith("__version__"):
                delimeter = '"' if '"' in line else "'"
                return line.split(delimeter)[1]
    raise RuntimeError("Cannot read version string.")
  
VERSION = _get_version()
  
setup(
  name = 'music_embedding', 
  packages = ['music_embedding'],
  version = VERSION,
  license='MIT',
  description = 'A package for representing music data based on music theory',
  author = 'SeyyedPooya HekmatiAthar',
  author_email = 's.pooyahekmati.a@gmail.com', 
  url = 'https://github.com/PooyaHekmati', 
  long_description=_get_long_description(),
  long_description_content_type="text/markdown",
  download_url = f'https://github.com/PooyaHekmati/music_embedding/archive/PyPI_v{VERSION}.tar.gz',
  project_urls={"Documentation": "https://pooyahekmati.github.io/music_embedding/"},
  keywords = ['music', 'interval', 'pianoroll', 'embedding', 'knowledge representation'], 
  install_requires=[
          'numpy',
      ],
  extras_require={
        "test": ["pytest>=6.0", "pytest-cov>=2.0"],
    },
  classifiers=[
    'Development Status :: 3 - Alpha',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable" 
    'Intended Audience :: Developers',    
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python :: 3',
  ],
  python_requires=">=3.6",
)
