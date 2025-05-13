from setuptools import setup, find_packages

setup(
    name="sommelier",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.22.0",
        "langchain-openai>=0.0.1",
        "python-dotenv>=0.19.0",
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI Chatbot application with LangChain and Streamlit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sommelier",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
