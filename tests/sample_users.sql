-- ユーザーテーブルのサンプルDDL（PostgreSQL形式）
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    age INT,
    balance DECIMAL(10,2),
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMP,
    birth_date DATE
);
