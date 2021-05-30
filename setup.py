from setuptools import setup

setup(
   name='CosmicAC',
   version='0.7.8',
   description='A discord.py discord bot',
   url="https://github.com/Frnot/The-Cosmic-AC",
   install_requires=[
      'aiosqlite',
      'discord.py',
      'python-dotenv',
      'importlib-metadata >= 1.0 ; python_version < "3.8"'
   ],
   python_requires='>=3.6',
   classifiers=[
      "Development Status :: 4 - Beta",
      "Programming Language :: Python :: 3",
      "Operating System :: OS Independent",
   ],
)
