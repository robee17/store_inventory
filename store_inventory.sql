-- Store Inventory System (with model number, size, and gender)
-- Import THIS .sql file in phpMyAdmin (Import tab) or paste it in the SQL tab.

CREATE DATABASE IF NOT EXISTS store_inventory_db;
USE store_inventory_db;

-- WARNING: this deletes the old products table so the new columns can be added.
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    product_id    INT AUTO_INCREMENT PRIMARY KEY,
    product_name  VARCHAR(60)   NOT NULL,
    category      VARCHAR(40)   NOT NULL,
    model_number  VARCHAR(30)   NOT NULL,
    size          VARCHAR(10)   NOT NULL,
    gender        VARCHAR(10)   NOT NULL,
    price         DECIMAL(10,2) NOT NULL,
    quantity      INT           NOT NULL,
    -- The same model in the same size and gender cannot be added twice
    UNIQUE (model_number, size, gender)
);

