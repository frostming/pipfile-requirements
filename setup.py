import io
from setuptools import setup

with io.open("README.md", encoding="utf-8") as f:
    README = f.read()


setup(
    name="pipfile-requirements",
    version="0.3.0",
    description="A CLI tool to covert Pipfile/Pipfile.lock to requirments.txt",
    url="https://github.com/frostming/pipfile-requirements",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Frost Ming",
    packages=["pipfile2req"],
    author_email="mianghong@gmail.com",
    license="MIT",
    install_requires=["toml", "packaging"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={"console_scripts": ["pipfile2req = pipfile2req.__main__:main"]},
)
