FROM python:3.10-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . /app

# 设置Flask环境变量
ENV FLASK_APP=api/app.py
ENV FLASK_RUN_PORT=7860

EXPOSE 7860

CMD ["flask", "run", "--host=0.0.0.0", "--port=7860"] 