FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir ".[postgres]" && useradd --create-home myops
USER myops

ENV MYOPS_PUBLIC_BASE_URL=http://127.0.0.1:8080
EXPOSE 8080
# Run `myops db upgrade` once per deploy (e.g. as a release step) before starting the server.
CMD ["myops", "serve", "--host", "0.0.0.0", "--port", "8080"]
