CREATE DATABASE IF NOT EXISTS threat_dashboard;

USE threat_dashboard;

CREATE TABLE IF NOT EXISTS phishing_urls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url TEXT,
    phish_id VARCHAR(100),
    online VARCHAR(20),
    target VARCHAR(100)
);

