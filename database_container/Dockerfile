FROM debian:latest

# Install sqlite3 and csvkit
RUN apt-get update && apt-get install -y \
    sqlite3 \
    csvkit \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/data

COPY . /app/data

# Expose port (not strictly necessary for SQLite, but good practice for database containers)
EXPOSE 5432

CMD ["tail", "-f", "/dev/null"]
