# 1. Use an official lightweight Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy your local files into the container
COPY . /app

# 4. Install pytest so the container can run your tests
RUN pip install pytest

# 5. The command to run when the container starts
CMD ["pytest", "-v"]