-- ユーザーテーブルのサンプルDDL
CREATE TABLE users (
    id INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    age INT,
    balance DECIMAL(10,2),
    is_active BOOLEAN NOT NULL,
    created_at DATETIME,
    birth_date DATE
);
