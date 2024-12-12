CREATE DATABASE IF NOT EXISTS pdf_rag_app;

USE pdf_rag_app;

-- Table for PDF & metadata
CREATE TABLE pdf_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context LONGTEXT
);

-- Table for user convos
CREATE TABLE user_conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_query TEXT NOT NULL,
    llm_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
