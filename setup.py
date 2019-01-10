import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hltex",
    version="0.0.2",
    author="Alex Gajewski & Wanqi Zhu",
    author_email="agajews@gmail.com",
    description="A compiler for HLTeX, a higher-level language on top of LaTeX",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agajews/hltex",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['scripts/hltex'],
    install_requires=['hlbox'],
)

