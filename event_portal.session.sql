CREATE TABLE event (
    event_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    time TIME,
    venue VARCHAR(100),
    organizer VARCHAR(100),
    max_seats INT
);