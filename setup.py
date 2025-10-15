from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='nfl_tracks',
    version='1.3.2',
    packages=find_packages(where="nfl_tracks"),
    package_dir={'': 'nfl_tracks'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    keywords="nfl, visualization, animated charts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "pandas",
        "matplotlib",
        "scipy",
        "seaborn"
    ],
    extras_require={
        "dev": ["pytest"],
    },
    url='https://github.com/shammeer-s/nfl-tracks',
    author='Mohammed Shammeer',
    author_email='mohammedshammeer.s@gmail.com',
    description='Python library written on top of matplotlib library for customizable nfl charts'
)