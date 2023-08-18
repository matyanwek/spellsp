import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="spellsp",
    version="0.1",
    description="A language server wrapper for spell checking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matyanwek/spellsp",
    author="Gal Zeira",
    author_email="gal_zeira@protonmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["spellsp = spellsp:main"]},
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
)
