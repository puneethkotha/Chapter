-- Insert topics first
INSERT INTO PJI_TOPIC (TOPIC_ID, TOPIC_NAME) VALUES
(1, 'Physics'),
(2, 'Science'),
(3, 'Art History'),
(4, 'Literature'),
(5, 'Technology'),
(6, 'Philosophy'),
(7, 'Psychology'),
(8, 'Business'),
(9, 'Mathematics'),
(10, 'Biology'),
(11, 'Quantum Physics'),
(12, 'Chemistry'),
(13, 'Computer Science'),
(14, 'Economics'),
(15, 'Geography'),
(16, 'Political Science'),
(17, 'Sociology'),
(18, 'Cultural Studies'),
(19, 'Environmental Studies'),
(20, 'Medicine');
-- Insert Authors
INSERT INTO PJI_AUTHOR (FNAME, LNAME, STREET, CITY, STATE, COUNTRY, POSTAL_CODE, EMAIL) VALUES
('John', 'Smith', '123 Oak St', 'New York', 'NY', 'USA', 10001, 'john.smith@email.com'),
('Emma', 'Johnson', '456 Maple Ave', 'Los Angeles', 'CA', 'USA', 90001, 'emma.j@email.com'),
('Michael', 'Brown', '789 Pine Rd', 'Chicago', 'IL', 'USA', 60601, 'mbrown@email.com'),
('Sarah', 'Davis', '321 Elm St', 'Houston', 'TX', 'USA', 77001, 'sarah.d@email.com'),
('David', 'Wilson', '654 Birch Ln', 'Phoenix', 'AZ', 'USA', 85001, 'dwilson@email.com'),
('Lisa', 'Anderson', '987 Cedar Dr', 'Philadelphia', 'PA', 'USA', 19101, 'lisa.a@email.com'),
('James', 'Taylor', '147 Spruce St', 'San Antonio', 'TX', 'USA', 78201, 'jtaylor@email.com'),
('Jennifer', 'Thomas', '258 Willow Ave', 'San Diego', 'CA', 'USA', 92101, 'jthomas@email.com'),
('Robert', 'Martinez', '369 Ash Rd', 'Dallas', 'TX', 'USA', 75201, 'rmartinez@email.com'),
('Patricia', 'Garcia', '741 Maple St', 'San Jose', 'CA', 'USA', 95101, 'pgarcia@email.com'),
('Daniel', 'Lee', '852 Oak Ave', 'Austin', 'TX', 'USA', 73301, 'dlee@email.com'),
('Michelle', 'Clark', '963 Pine Ln', 'Jacksonville', 'FL', 'USA', 32201, 'mclark@email.com'),
('Christopher', 'Rodriguez', '159 Elm Dr', 'San Francisco', 'CA', 'USA', 94101, 'crodriguez@email.com'),
('Elizabeth', 'Lewis', '357 Birch St', 'Indianapolis', 'IN', 'USA', 46201, 'elewis@email.com'),
('Joseph', 'Walker', '486 Cedar Ave', 'Columbus', 'OH', 'USA', 43201, 'jwalker@email.com'),
('Margaret', 'Hall', '159 Spruce Rd', 'Fort Worth', 'TX', 'USA', 76101, 'mhall@email.com'),
('Kevin', 'Allen', '753 Willow St', 'Charlotte', 'NC', 'USA', 28201, 'kallen@email.com'),
('Nancy', 'Young', '951 Ash Ave', 'Detroit', 'MI', 'USA', 48201, 'nyoung@email.com'),
('Steven', 'King', '357 Maple Dr', 'El Paso', 'TX', 'USA', 79901, 'sking@email.com'),
('Barbara', 'Wright', '486 Oak Ln', 'Seattle', 'WA', 'USA', 98101, 'bwright@email.com');
-- Now insert books with valid topic IDs
INSERT INTO PJI_BOOK (BOOK_ID, BOOK_NAME, PJI_TOPIC_TOPIC_ID) VALUES
(1, 'The History of Time', 1),
(2, 'Modern Physics', 2),
(3, 'Art in Renaissance', 3),
(4, 'Classic Literature', 4),
(5, 'Digital Revolution', 5),
(6, 'Philosophy of Mind', 6),
(7, 'Understanding Psychology', 7),
(8, 'Business Strategy', 8),
(9, 'Advanced Mathematics', 9),
(10, 'Human Biology', 10),
(11, 'Quantum Mechanics', 11),
(12, 'Organic Chemistry', 12),
(13, 'Programming Basics', 13),
(14, 'Microeconomics', 14),
(15, 'World Geography', 15),
(16, 'Political Systems', 16),
(17, 'Social Structures', 17),
(18, 'Cultural Studies', 18),
(19, 'Environmental Science', 19),
(20, 'Medical Practice', 20);
-- Insert Book Copies (2 copies per book)
INSERT INTO PJI_BOOK_COPY (STATUS, PJI_BOOK_BOOK_ID)
SELECT 'available', BOOK_ID FROM PJI_BOOK
UNION ALL
SELECT 'available', BOOK_ID FROM PJI_BOOK;
-- Insert Book Authors (Multiple authors per book)
INSERT INTO PJI_BOOK_AUTHOR (PJI_BOOK_BOOK_ID, PJI_AUTHOR_AUTHOR_ID)
SELECT b.BOOK_ID, a.AUTHOR_ID
FROM PJI_BOOK b
CROSS JOIN PJI_AUTHOR a
WHERE (b.BOOK_ID + a.AUTHOR_ID) % 5 = 0
LIMIT 20;
-- Insert Customers
INSERT INTO PJI_CUSTOMER (FNAME, LNAME, PHONE, EMAIL, ID_TYPE, ID_NO) VALUES
('Alice', 'Johnson', '555-0101', 'alice.j@email.com', 'Passport', 'P123456'),
('Bob', 'Smith', '555-0102', 'bob.s@email.com', 'SSN', 'S123456'),
('Carol', 'Williams', '555-0103', 'carol.w@email.com', 'Driver License', 'D123456'),
('David', 'Brown', '555-0104', 'david.b@email.com', 'Passport', 'P234567'),
('Eve', 'Davis', '555-0105', 'eve.d@email.com', 'SSN', 'S234567'),
('Frank', 'Miller', '555-0106', 'frank.m@email.com', 'Driver License', 'D234567'),
('Grace', 'Wilson', '555-0107', 'grace.w@email.com', 'Passport', 'P345678'),
('Henry', 'Moore', '555-0108', 'henry.m@email.com', 'SSN', 'S345678'),
('Ivy', 'Taylor', '555-0109', 'ivy.t@email.com', 'Driver License', 'D345678'),
('Jack', 'Anderson', '555-0110', 'jack.a@email.com', 'Passport', 'P456789'),
('Kelly', 'Thomas', '555-0111', 'kelly.t@email.com', 'SSN', 'S456789'),
('Liam', 'Jackson', '555-0112', 'liam.j@email.com', 'Driver License', 'D456789'),
('Mia', 'White', '555-0113', 'mia.w@email.com', 'Passport', 'P567890'),
('Noah', 'Harris', '555-0114', 'noah.h@email.com', 'SSN', 'S567890'),
('Olivia', 'Martin', '555-0115', 'olivia.m@email.com', 'Driver License', 'D567890'),
('Peter', 'Thompson', '555-0116', 'peter.t@email.com', 'Passport', 'P678901'),
('Quinn', 'Garcia', '555-0117', 'quinn.g@email.com', 'SSN', 'S678901'),
('Ryan', 'Martinez', '555-0118', 'ryan.m@email.com', 'Driver License', 'D678901'),
('Sofia', 'Robinson', '555-0119', 'sofia.r@email.com', 'Passport', 'P789012'),
('Tyler', 'Clark', '555-0120', 'tyler.c@email.com', 'SSN', 'S789012');
-- Insert Rentals and Invoices (will be generated by trigger)
INSERT INTO PJI_RENTAL (STATUS, BORROW_DATE, EXP_RETURN_DT, PJI_CUSTOMER_CUST_ID,
PJI_BOOK_COPY_COPY_ID)
SELECT
'Borrowed',
DATE_SUB(NOW(), INTERVAL FLOOR(1 + RAND() * 30) DAY),
DATE_ADD(NOW(), INTERVAL FLOOR(1 + RAND() * 14) DAY),
c.CUST_ID,
bc.COPY_ID
FROM
PJI_CUSTOMER c
CROSS JOIN PJI_BOOK_COPY bc
WHERE
bc.STATUS = 'available'
LIMIT 20;
-- Update some rentals to Returned to trigger invoice generation
UPDATE PJI_RENTAL
SET
STATUS = 'Returned',
ACTUAL_RETURN_DT = DATE_ADD(BORROW_DATE, INTERVAL FLOOR(1 + RAND() * 14) DAY)
WHERE
RENTAL_ID <= 10;
-- Insert Payments
INSERT INTO PJI_PAYMENT (PAYMENT_DATE, PAY_METHOD, CARDHOLDER_NAME, PAYMENT_AMT,
PJI_INVOICE_INVOICE_ID)
SELECT
NOW(),
CASE
WHEN (i.INVOICE_ID % 4) = 0 THEN 'Cash'
WHEN (i.INVOICE_ID % 4) = 1 THEN 'Credit'
WHEN (i.INVOICE_ID % 4) = 2 THEN 'Debit'
ELSE 'PayPal'
END as PAY_METHOD,
CASE
WHEN (i.INVOICE_ID % 4) IN (1, 2) THEN CONCAT(c.FNAME, ' ', c.LNAME)
ELSE NULL
END as CARDHOLDER_NAME,
i.INVOICE_AMT,
i.INVOICE_ID
FROM
PJI_INVOICE i
JOIN PJI_RENTAL r ON i.INVOICE_ID = r.PJI_INVOICE_INVOICE_ID
JOIN PJI_CUSTOMER c ON r.PJI_CUSTOMER_CUST_ID = c.CUST_ID
LIMIT 20;
-- Insert Study Rooms
INSERT INTO PJI_STUDY_ROOM (ROOM_ID, CAPACITY) VALUES
(1, 4), (2, 6), (3, 8), (4, 4), (5, 6),
(6, 8), (7, 4), (8, 6), (9, 8), (10, 4),
(11, 6), (12, 8), (13, 4), (14, 6), (15, 8),
(16, 4), (17, 6), (18, 8), (19, 4), (20, 6);
-- Insert Events (10 Exhibitions and 10 Seminars)
INSERT INTO PJI_EVENT (EVENT_ID, EVENT_NAME, START_DT, END_DT, ATTD_NO, EVENT_TYPE) VALUES
-- Exhibitions
(1, 'Modern Art Exhibition', '2024-04-01 10:00:00', '2024-04-15 18:00:00', 100, 'E'),
(2, 'Science Fair 2024', '2024-04-15 09:00:00', '2024-04-20 17:00:00', 150, 'E'),
(3, 'Historical Documents Display', '2024-05-01 10:00:00', '2024-05-10 18:00:00', 80, 'E'),
(4, 'Photography Exhibition', '2024-05-15 09:00:00', '2024-05-25 17:00:00', 120, 'E'),
(5, 'Technology Showcase', '2024-06-01 10:00:00', '2024-06-10 18:00:00', 200, 'E'),
(6, 'Book Art Exhibition', '2024-06-15 09:00:00', '2024-06-25 17:00:00', 90, 'E'),
(7, 'Environmental Awareness Display', '2024-07-01 10:00:00', '2024-07-10 18:00:00', 110, 'E'),
(8, 'Cultural Heritage Exhibition', '2024-07-15 09:00:00', '2024-07-25 17:00:00', 130, 'E'),
(9, 'Digital Art Show', '2024-08-01 10:00:00', '2024-08-10 18:00:00', 140, 'E'),
(10, 'Architecture Models Display', '2024-08-15 09:00:00', '2024-08-25 17:00:00', 160, 'E'),
-- Seminars
(11, 'Writing Workshop', '2024-04-05 14:00:00', '2024-04-05 17:00:00', 50, 'S'),
(12, 'Research Methodology', '2024-04-20 13:00:00', '2024-04-20 16:00:00', 40, 'S'),
(13, 'Digital Marketing', '2024-05-05 14:00:00', '2024-05-05 17:00:00', 45, 'S'),
(14, 'Data Analysis', '2024-05-20 13:00:00', '2024-05-20 16:00:00', 35, 'S'),
(15, 'Public Speaking', '2024-06-05 14:00:00', '2024-06-05 17:00:00', 30, 'S'),
(16, 'Project Management', '2024-06-20 13:00:00', '2024-06-20 16:00:00', 40, 'S'),
(17, 'Creative Writing', '2024-07-05 14:00:00', '2024-07-05 17:00:00', 25, 'S'),
(18, 'Business Strategy', '2024-07-20 13:00:00', '2024-07-20 16:00:00', 45, 'S'),
(19, 'Leadership Skills', '2024-08-05 14:00:00', '2024-08-05 17:00:00', 35, 'S'),
(20, 'Innovation Workshop', '2024-08-20 13:00:00', '2024-08-20 16:00:00', 40, 'S');
-- Insert Exhibitions
INSERT INTO PJI_EXHIBITION (EVENT_ID, EXPENSES) VALUES
(1, 5000.00), (2, 7500.00), (3, 3000.00), (4, 4500.00), (5, 8000.00),
(6, 3500.00), (7, 4000.00), (8, 5500.00), (9, 6000.00), (10, 7000.00);
-- Insert Seminars
INSERT INTO PJI_SEMINAR (EVENT_ID, EST_AUTH) VALUES
(11, 3), (12, 2), (13, 2), (14, 3), (15, 1),
(16, 2), (17, 2), (18, 3), (19, 2), (20, 2);
-- Insert Sponsors (10 Individual and 10 Organization)
INSERT INTO PJI_SPONSOR (SPONSOR_ID, SPONSOR_TYPE) VALUES
-- Individual Sponsors
(1, 'I'), (2, 'I'), (3, 'I'), (4, 'I'), (5, 'I'),
(6, 'I'), (7, 'I'), (8, 'I'), (9, 'I'), (10, 'I'),
-- Organization Sponsors
(11, 'O'), (12, 'O'), (13, 'O'), (14, 'O'), (15, 'O'),
(16, 'O'), (17, 'O'), (18, 'O'), (19, 'O'), (20, 'O');
-- Insert Individual Sponsors
INSERT INTO PJI_INDIVIDUAL (SPONSOR_ID, FNAME, LNAME) VALUES
(1, 'John', 'Doe'), (2, 'Jane', 'Smith'), (3, 'Robert', 'Johnson'),
(4, 'Mary', 'Williams'), (5, 'David', 'Brown'), (6, 'Sarah', 'Davis'),
(7, 'Michael', 'Wilson'), (8, 'Emily', 'Taylor'), (9, 'James', 'Anderson'),
(10, 'Lisa', 'Thomas');
-- Insert Organization Sponsors
INSERT INTO PJI_ORG (SPONSOR_ID, ORG_NAME) VALUES
(11, 'Tech Solutions Inc.'), (12, 'Global Education Foundation'),
(13, 'Creative Arts Society'), (14, 'Science Research Institute'),
(15, 'Business Development Corp'), (16, 'Cultural Heritage Trust'),
(17, 'Environmental Protection Agency'), (18, 'Digital Innovation Hub'),
(19, 'Leadership Academy'), (20, 'Future Learning Center');
-- Insert Seminar Sponsors
INSERT INTO PJI_SEM_SPONSOR (PJI_SEMINAR_EVENT_ID, PJI_SPONSOR_SPONSOR_ID, AMOUNT) VALUES
(11, 1, 1000.00), (12, 11, 1500.00), (13, 2, 1200.00),
(14, 12, 1800.00), (15, 3, 800.00), (16, 13, 2000.00),
(17, 4, 900.00), (18, 14, 1600.00), (19, 5, 1100.00),
(20, 15, 1700.00);
-- Insert Study Room Reservations
INSERT INTO PJI_RESERVATION (RESERVE_ID, TOPIC_DESC, START_DT, END_DT, GROUP_SIZE,
PJI_CUSTOMER_CUST_ID, PJI_STUDY_ROOM_ROOM_ID)
WITH RECURSIVE dates AS (
SELECT
ROW_NUMBER() OVER (ORDER BY c.CUST_ID) as RESERVE_ID,
c.CUST_ID,
r.ROOM_ID,
FLOOR(1 + RAND() * 8) as GROUP_SIZE,
DATE_ADD(NOW(), INTERVAL FLOOR(1 + RAND() * 30) DAY) as START_DT,
DATE_ADD(NOW(), INTERVAL FLOOR(1 + RAND() * 30 + 2) DAY) as END_DT
FROM
PJI_CUSTOMER c
CROSS JOIN PJI_STUDY_ROOM r
WHERE
r.CAPACITY >= FLOOR(1 + RAND() * 8)
)
SELECT
RESERVE_ID,
CONCAT('Study Session ', RESERVE_ID),
START_DT,
END_DT,
GROUP_SIZE,
CUST_ID,
ROOM_ID
FROM
dates
WHERE
END_DT > START_DT
LIMIT 20;
-- Insert Exhibition Attendance
INSERT INTO PJI_EXH_ATTD (REG_ID, PJI_EXHIBITION_EVENT_ID, PJI_CUSTOMER_CUST_ID)
SELECT
ROW_NUMBER() OVER (ORDER BY e.EVENT_ID) as REG_ID,
e.EVENT_ID,
c.CUST_ID
FROM
PJI_EXHIBITION e
CROSS JOIN PJI_CUSTOMER c
WHERE
(e.EVENT_ID + c.CUST_ID) % 3 = 0
LIMIT 20;
-- Insert Seminar Attendance
INSERT INTO PJI_SEMINAR_ATTD (INVITATION_ID, PJI_AUTHOR_AUTHOR_ID, PJI_SEMINAR_EVENT_ID)
SELECT
ROW_NUMBER() OVER (ORDER BY s.EVENT_ID) as INVITATION_ID,
a.AUTHOR_ID,
s.EVENT_ID
FROM
PJI_SEMINAR s
CROSS JOIN PJI_AUTHOR a
WHERE
(s.EVENT_ID + a.AUTHOR_ID) % 3 = 0
LIMIT 20;