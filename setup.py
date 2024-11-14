from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='nfl',
    version='1.0.0',
    packages=find_packages(where="src"),
    package_dir={'': 'src'},
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
        "pandas~=2.2.2",
        "setuptools~=75.1.0",
        "matplotlib~=3.9.2"
    ],
    extras_require={
        "dev": [
            "pytest >= 6.2.5"
        ]
    },
    url='https://github.com/shammeer-s/nfl-viz',
    author='Mohammed Shammeer',
    author_email='mohammedshammeer.s@gmail.com',
    description='Python library written on top of matplotlib library for customizable nfl charts'
)