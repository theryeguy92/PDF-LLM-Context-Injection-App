FROM mysql:latest

# Set root password, database name, and user
ENV MYSQL_ROOT_PASSWORD=rootpassword
ENV MYSQL_DATABASE=pdf_rag_app
ENV MYSQL_USER=admin
ENV MYSQL_PASSWORD=password

# SQL SCHEMA
COPY schema.sql /docker-entrypoint-initdb.d/
