FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    gfortran \
    make \
    git \
    vim \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY requirements.txt .
COPY Makefile .
COPY src/ src/
COPY docs/ docs/
COPY examples/ examples/
COPY data/ data/
COPY tests/ tests/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Compile Fortran modules
RUN make fortran

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Default command
CMD ["/bin/bash"]
