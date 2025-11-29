-- Schema: Event Registration & Feedback Admin Portal

CREATE DATABASE IF NOT EXISTS event_admin;
USE event_admin;

DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS registration;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS event;

CREATE TABLE event (
    event_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    date DATE,
    time TIME,
    venue VARCHAR(100),
    organizer VARCHAR(100),
    max_seats INT,
    registration_count INT DEFAULT 0
);

CREATE TABLE student (
    USN INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(15)
);

CREATE TABLE registration (
    reg_id INT PRIMARY KEY,
    event_id INT,
    USN INT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE CASCADE,
    FOREIGN KEY (USN) REFERENCES student(USN) ON DELETE CASCADE
);

CREATE TABLE feedback (
    feedback_id INT PRIMARY KEY,
    event_id INT,
    USN INT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment VARCHAR(255),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES event(event_id) ON DELETE CASCADE,
    FOREIGN KEY (USN) REFERENCES student(USN) ON DELETE CASCADE
);

DELIMITER //
CREATE TRIGGER increment_registration_count
AFTER INSERT ON registration
FOR EACH ROW
BEGIN
    UPDATE event
    SET registration_count = IFNULL(registration_count, 0) + 1
    WHERE event_id = NEW.event_id;
END;//
DELIMITER ;

-- Optional helper trigger to keep counts in sync after delete
DELIMITER //
CREATE TRIGGER decrement_registration_count
AFTER DELETE ON registration
FOR EACH ROW
BEGIN
    UPDATE event
    SET registration_count = GREATEST(IFNULL(registration_count, 1) - 1, 0)
    WHERE event_id = OLD.event_id;
END;//
DELIMITER ;

-- Sample seed data
INSERT INTO event VALUES
(1, 'Tech Talk on AI', 'Recent advancements in AI', '2025-01-15', '10:00:00', 'Auditorium', 'CSE Dept', 200, 0),
(2, 'Python Workshop', 'Hands-on Python basics', '2025-02-10', '14:00:00', 'Lab 5', 'IT Dept', 60, 0),
(3, 'Hackathon', '24-hour coding challenge', '2025-03-20', '09:00:00', 'Innovation Lab', 'Tech Club', 120, 0);

INSERT INTO student VALUES
(1001, 'Deepika', 'CSE', 'deepika@example.com', '9876543210'),
(1002, 'Arun Kumar', 'CSE', 'arun@example.com', '9876501234'),
(1003, 'Meera R', 'IT', 'meera@example.com', '9087654321');

INSERT INTO registration VALUES
(5001, 1, 1001, '2024-12-30 09:20:00'),
(5002, 1, 1002, '2024-12-30 09:40:00'),
(5003, 2, 1003, '2025-01-15 10:10:00');

INSERT INTO feedback VALUES
(9001, 1, 1001, 5, 'Great event, well organized!', '2024-12-30 11:00:00'),
(9002, 2, 1003, 4, 'Loved the workshop!', '2025-01-15 12:00:00');
