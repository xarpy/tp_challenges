# # Base on offical from Playwirght image
FROM mcr.microsoft.com/playwright/python:v1.38.0-jammy
# Set working directory
WORKDIR /telescopes
# Copy all files
COPY . .
# Update packages and installdependecies
RUN apt update
# Install dependencies
RUN pip install --upgrade pip && pip install --require-hashes -r /telescopes/requirements/dev.txt
# Install spacy dependencies
RUN python3 -m spacy download en_core_web_sm
