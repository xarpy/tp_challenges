# # Base on offical Python Slim image
FROM python:3.10-slim
# Set working directory
WORKDIR /telescopes
# Copy all files
COPY . .
# Install dependencies
RUN pip install --upgrade pip && pip install --require-hashes -r /telescopes/requirements/dev.txt && python -m spacy download en_core_web_sm && playwright install
# Install  system dependencies
RUN apt-get update && \
    apt-get install -y xvfb x11-apps x11-xkb-utils libx11-6 libx11-xcb1
# Install playwright depedencies
RUN playwright install-deps
