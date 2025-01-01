# Use the official Python image from the Docker Hub
FROM python:3.12-alpine as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES \
    AWS_REGION=ap-south-1

# Install dependencies
RUN apk --no-cache add \
    gcc python3-dev musl-dev linux-headers \
    postgresql-dev libpq pango \
    zlib-dev jpeg-dev openjpeg-dev g++ libffi-dev harfbuzz-subset \
    && apk --no-cache add redis

# Create a non-root user and group
RUN addgroup -S insightgroup && adduser -S insightsol -G insightgroup

# Set working directory
WORKDIR /backend

# Copy the requirements.txt first to leverage Docker cache for dependencies
COPY requirements.txt /backend/

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project files
COPY . /backend/

# Collect static files
RUN python manage.py collectstatic --noinput

# Adjust ownership of the working directory
RUN chown -R insightsol:insightgroup /backend

# Switch to the non-root user
USER insightsol

# Final command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "insightsol.wsgi:application"]
