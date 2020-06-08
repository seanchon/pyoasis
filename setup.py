from setuptools import setup, find_packages

setup(
    name="pyoasis",
    version="0.1.0",
    description="""Python interface to CAISO's OASIS API.""",
    url="git@github.com:TerraVerdeRenewablePartners/pyoasis.git",
    author="Sean Chon",
    author_email="sean@terraverde.energy",
    license="N/A",
    packages=find_packages(),
    install_requires=["cached-property", "pandas", "requests", "xmltodict"],
    package_data={"": ["*.json", "*.txt"]},
    zip_safe=False,
)
