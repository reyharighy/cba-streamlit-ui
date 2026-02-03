FROM python:3.12

RUN pip install --no-cache-dir uv --root-user-action=ignore

ARG WORKDIR_PATH
WORKDIR ${WORKDIR_PATH}

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . ./

RUN useradd -m -u 1000 streamlituser
RUN chown -R streamlituser:streamlituser ${WORKDIR_PATH}

USER streamlituser

ARG STREAMLIT_PORT
EXPOSE ${STREAMLIT_PORT}

ENV STREAMLIT_PORT=${STREAMLIT_PORT}

CMD ["sh", "-c", "uv run streamlit run main.py --server.port=${STREAMLIT_PORT} --server.address=0.0.0.0 --server.runOnSave=true"]
