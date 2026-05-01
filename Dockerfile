# 1. Берем основу: «компьютер» с уже установленным Python
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1

# 2. Создаем рабочую папку внутри этого «компьютера»
WORKDIR /crypto_pipeline

# 3. Копируем список библиотек и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем наш скрипт внутрь
COPY main.py .

# 5. Команда, которую нужно выполнить при включении этого «компьютера»
CMD ["python", "main.py"]