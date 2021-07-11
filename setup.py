from setuptools import setup

setup(
   name='CosmicAC',
   version='2.0.0-1',
   description='A discord.py discord bot',
   url="https://github.com/Frnot/The-Cosmic-AC",
   install_requires=[
      'aiosqlite',
      'discord.py',
      'python-dotenv',
      'importlib-metadata >= 1.0 ; python_version < "3.8"',
      'fuzzysearch',
      'python-Levenshtein'
   ],
   python_requires='>=3.6',
   classifiers=[
      "Development Status :: 4 - Beta",
      "Programming Language :: Python :: 3",
      "Operating System :: OS Independent",
   ],
)
