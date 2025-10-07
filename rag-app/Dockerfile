FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin
ENV PATH="/app/.venv/bin:$PATH"

# Install dependencies only
COPY service/pyproject.toml service/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Copy application code
COPY service/ /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Run app
ENTRYPOINT ["uv"]
CMD ["run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
