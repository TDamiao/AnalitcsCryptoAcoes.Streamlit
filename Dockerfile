# Usar uma imagem base do Python
FROM python:3.11-slim

# Definir o diretório de trabalho
WORKDIR /app

# Copiar o arquivo de requisitos para o contêiner
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação para o contêiner
COPY app.py .

# Expor a porta usada pelo Streamlit
EXPOSE 8501

# Comando para rodar a aplicação Streamlit
CMD ["streamlit", "run", "app.py"]