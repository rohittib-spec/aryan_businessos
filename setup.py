from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="aryan_businessos",
    version="1.0.0",
    description="Aryan BusinessOS — Industry ERP for Indian SMEs",
    author="Aryan Consulting",
    author_email="info@aryanconsulting.in",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
