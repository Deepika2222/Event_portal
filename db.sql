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
CREATE TABLE student (
    USN INT  PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15)
);
CREATE TABLE registration (
    reg_id INT  PRIMARY KEY,
    event_id INT,
    USN INT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES event(event_id) on delete cascade,
    FOREIGN KEY (USN) REFERENCES student(USN) on delete cascade
);
drop table users;
CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT,
    USN INT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment VARCHAR(255),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES event(event_id),
    FOREIGN KEY (USN) REFERENCES student(USN)
);
INSERT INTO event VALUES(1, 'Tech Talk on AI', 'Session on recent advancements in AI', '2025-01-15', '10:00:00', 'Auditorium', 'CSE Dept', 200);

INSERT INTO event VALUES(2, 'Python Workshop', 'Hands-on Python basics workshop', '2025-02-10', '14:00:00', 'Lab 5', 'IT Dept', 60);

INSERT INTO event VALUES(3, 'Hackathon', '24-hour coding challenge', '2025-03-20', '09:00:00', 'Innovation Lab', 'Tech Club', 120);

INSERT INTO event VALUES(4, 'Data Science Seminar', 'Exploring data science techniques', '2025-04-05', '11:00:00', 'Conference Room', 'Data Club', 80);

INSERT INTO event VALUES(5, 'Cybersecurity Workshop', 'Basics of cybersecurity practices', '2025-05-12', '15:00:00', 'Lab 3', 'Security Team', 50);
INSERT INTO student VALUES('11', 'Deepika',  'CSE', 'deepika@example.com', '9876543210');

INSERT INTO student VALUES('12', 'Arun Kumar',  'CSE', 'arun@example.com', '9876501234');

INSERT INTO student VALUES('13', 'Meera R', 'IT', 'meera@example.com', '9087654321');

-- INSERT INTO student VALUES('14', 'Rahul Singh', 'ECE', 'rahul@example.com', '9988776655');
INSERT INTO registration VALUES (101, 1, 11, '2025-01-10 10:30:00');

INSERT INTO registration VALUES (102, 1, 12, '2025-01-10 11:00:00');

INSERT INTO registration VALUES (103, 2, 11, '2025-02-05 14:15:00');

INSERT INTO registration VALUES (105, 3, 14, '2025-03-15 09:45:00');

INSERT INTO registration VALUES (106, 4, 13, '2025-04-01 16:20:00');

INSERT INTO feedback VALUES(1001,1,11,5, 'Great event, very well organized!', '2025-01-10 10:30:00');

INSERT INTO feedback VALUES(1002,2,12,4, 'Good session but could have been longer.', '2025-01-10 11:00:00');

INSERT INTO feedback VALUES(1006,3,11,3, 'Average experience, needs improvement.', '2025-02-05 14:45:00');

INSERT INTO feedback VALUES(1003,4,14,5, 'Loved it! Very interactive.', '2025-03-12 09:20:00');

INSERT INTO feedback VALUES(1004,5,13,4, 'Useful but the venue was crowded.', '2025-04-18 16:10:00');
 SELECT * FROM student;
    SELECT * FROM event;
    SELECT * FROM registration;
    SELECT * FROM feedback;
SELECT r.reg_id, s.name AS student_name, e.name, r.registration_date
FROM registration r
JOIN student s ON r.USN = s.USN
JOIN event e ON r.event_id = e.event_id;

SELECT f.feedback_id, s.name, e.name, f.rating, f.comment
FROM feedback f
JOIN student s ON f.USN = s.USN
JOIN event e ON f.event_id = e.event_id;

CREATE TRIGGER increment_registration_count
AFTER INSERT ON registration
FOR EACH ROW
BEGIN
    UPDATE event
    SET registration_count = registration_count + 1
    WHERE event_id = NEW.event_id;
END;
SHOW TRIGGERS LIKE 'event';




