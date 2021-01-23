from distutils.core import setup
setup(
  name = 'music_embedding', 
  packages = ['music_embedding'],
  version = '0.1.2',
  license='MIT',
  description = 'A package for representing music data based on music theory',
  author = 'SeyyedPooya HekmatiAthar',
  author_email = 's.pooyahekmati.a@gmail.com', 
  url = 'https://github.com/PooyaHekmati', 
  download_url = 'https://github.com/PooyaHekmati/music_embedding/archive/PyPI_v0.1.2.tar.gz',
  keywords = ['music', 'interval', 'pianoroll', 'embedding', 'knowledge representation'], 
  install_requires=[
          'numpy',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable" 
    'Intended Audience :: Developers',    
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License', 
    'Programming Language :: Python :: 3',   
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)