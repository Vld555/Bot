# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл requirements.txt в рабочую директорию
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все остальные файлы в рабочую директорию
COPY . .

# Запускаем бота
CMD ["python", "bot.py"]
