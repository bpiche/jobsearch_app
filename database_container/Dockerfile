FROM debian:latest

# Install sqlite3 and csvkit
RUN apt-get update && apt-get install -y \
    sqlite3 \
    csvkit \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/data

COPY data/ai_job_dataset.csv ai_job_dataset.csv

# Create SQLite database from CSV
RUN csvsql --db sqlite:///ai_jobs.db --insert ai_job_dataset.csv && \
    echo "Database created successfully."

# Validate database creation (e.g., count rows in a table)
RUN sqlite3 ai_jobs.db "SELECT 'Validation successful: ' || count(*) || ' rows in ai_job_dataset' FROM ai_job_dataset;" || \
    (echo "Database validation failed!" && exit 1)

# Expose port (not strictly necessary for SQLite, but good practice for database containers)
EXPOSE 5432

CMD ["tail", "-f", "/dev/null"]
