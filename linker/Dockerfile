FROM python:3.12 AS builder

ENV PIP_DEFAULT_TIMEOUT=200 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 

ENV RYE_HOME="/opt/rye"
ENV PATH="$RYE_HOME/shims:$PATH"
ENV UV_HTTP_TIMEOUT=1200
ENV WD_NAME=/app
WORKDIR $WD_NAME
RUN curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" \
                                          RYE_NO_AUTO_INSTALL=1  \
                                          bash \
&& rye config --set-bool behavior.use-uv=true \
&& rye config --set-bool autosync=false


COPY linker/.python-version* .python-version
COPY linker/README.md README.md
COPY linker/pyproject.toml pyproject.toml
COPY linker/requirements.lock* requirements.lock

COPY openai_api openai_api
COPY shared shared
RUN rye add openai_api --path openai_api
RUN rye add shared --path shared

RUN rye sync --no-lock --no-dev

ENV PATH="$WD_NAME/.venv/bin:$PATH"

FROM python:3.12-slim as runtime

ENV WD_NAME=/app
WORKDIR $WD_NAME

ENV PATH="$WD_NAME/.venv/bin:$PATH"
ENV PYTHONPATH="$PYTHONPATH:$WD_NAME/.venv/lib/python3.12/site-packages"

COPY --from=builder /opt/rye /opt/rye
COPY --from=builder $WD_NAME/.venv .venv
COPY --from=builder $WD_NAME/shared shared
COPY --from=builder $WD_NAME/openai_api openai_api
COPY linker/src src
ENTRYPOINT ["uvicorn", "--app-dir", "src", "--host", "0.0.0.0", "main:app"]
