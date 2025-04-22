PRAGMA foreign_keys = off;

DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
    user_id varchar(8) not null,
    username varchar(50) unique not null,
    password varchar(50) not null, 
    role varchar(50) not null,
    primary key (user_id)
);

DROP TABLE IF EXISTS PersonalInfo;
CREATE TABLE PersonalInfo (
    ssn varchar(15) not null,
    fname varchar(50) not null,
    lname varchar(50) not null,
    address varchar(50) not null,
    phone varchar(50) not null,
    email varchar(50) not null,
    primary key (ssn)
);

DROP TABLE IF EXISTS Applicants;
CREATE TABLE Applicants (
    app_id varchar(8) not null,
    ssn varchar(15) unique not null,
    degree_sought varchar(50) not null,
    admission_term varchar(50) not null,
    admission_year INTEGER not null, 
    gre_verbal INTEGER, 
    gre_quantitative INTEGER, 
    gre_subject INTEGER, 
    work_experience varchar(50),
    transcript_received BOOLEAN default 0,
    application_status varchar(50) default 'Application Incomplete', 
    primary key (app_id),
    foreign key (app_id) references Users (user_id),
    foreign key (ssn) references PersonalInfo (ssn)
);

DROP TABLE IF EXISTS PriorDegrees;
CREATE TABLE PriorDegrees (
    user_id varchar(8) not null,
    bachelors BOOLEAN default 0, 
    bachelors_university varchar(50) not null,
    bachelors_grad_year INTEGER not null,
    bachelors_major varchar(50) not null,
    bachelors_gpa REAL not null,
    masters BOOLEAN default 0,
    masters_university varchar(50),
    masters_grad_year INTEGER,
    masters_major varchar(50),
    masters_gpa REAL,
    primary key (user_id),
    foreign key (user_id) references Applicants (app_id)
);

DROP TABLE IF EXISTS RecommendationLetters;
CREATE TABLE RecommendationLetters (
    user_id varchar(8) not null,
    recommender_name varchar(50) not null,
    email varchar(50) not null,
    title varchar(50),
    affiliation varchar(50),
    primary key (user_id),
    foreign key (user_id) references Applicants (app_id)
);

DROP TABLE IF EXISTS Reviews;
CREATE TABLE Reviews (
    app_id varchar(8) not null,
    reviewer_id varchar(8) not null,
    ranking INTEGER not null,
    comments varchar(50),
    recommended_advisor varchar(50),
    reject_reason varchar(1),
    primary key (app_id, reviewer_id),
    foreign key (app_id) references Applicants (app_id),
    foreign key (reviewer_id) references Users (user_id)
);

DROP TABLE IF EXISTS FinalDecisions;
CREATE TABLE FinalDecisions (
    user_id varchar(8) not null,
    decided_by varchar(8) not null,
    decision varchar(50) not null,
    primary key (user_id),
    foreign key (user_id) references Applicants (user_id),
    foreign key (decided_by) references Users (user_id)
);

PRAGMA foreign_keys = on;

-- Applicants Users
INSERT INTO Users (user_id, username, password, role)
VALUES ('12312312', 'John', 'JohnLennon123', 'Applicant');
INSERT INTO Users (user_id, username, password, role)
VALUES ('66666666', 'Ringo', 'RingoStarr123', 'Applicant');

-- Personal Info
INSERT INTO PersonalInfo (ssn, fname, lname, address, phone, email)
VALUES ('111-11-1111', 'John', 'Lennon', '1234 Address Lane', '202-303-4040', 'jlennon25@gmail.com');
INSERT INTO PersonalInfo (ssn, fname, lname, address, phone, email)
VALUES ('222-11-1111', 'Ringo', 'Starr', '5678 Address Lane', '505-606-7070', 'rstarr25@gmail.com');

-- Faculty Users
INSERT INTO Users (user_id, username, password, role)
VALUES ('00000001', 'Peter', 'GS_ADMIN', 'GS');
INSERT INTO Users (user_id, username, password, role)
VALUES ('00000002', 'Gabriel', 'CAC_ADMIN', 'CAC');
INSERT INTO Users (user_id, username, password, role)
VALUES ('00000003', 'Narahari', 'Narahari123', 'Reviewer');
INSERT INTO Users (user_id, username, password, role)
VALUES ('00000004', 'Wood', 'Wood123', 'Reviewer');
INSERT INTO Users (user_id, username, password, role)
VALUES ('00000005', 'Heller', 'Heller123', 'Reviewer');

-- Applicants
INSERT INTO Applicants 
    (app_id, ssn, degree_sought, admission_term, admission_year, gre_verbal, gre_quantitative, gre_subject, work_experience, transcript_received, application_status)
VALUES 
    ('12312312', '111-11-1111', 'PhD', 'Fall', 2025, 160, 165, 700, 'Worked at McDonalds 12 years', 1, 'Application Complete and Under Review/No Decision Yet');
INSERT INTO Applicants 
    (app_id, ssn, degree_sought, admission_term, admission_year, work_experience, transcript_received, application_status)
VALUES 
    ('66666666', '222-11-1111', 'MS', 'Spring', 2025, 'Singer for 24 years', 0, 'Application Incomplete');

-- Reviews
INSERT INTO Reviews
    (app_id, reviewer_id, ranking, comments, recommended_advisor, reject_reason)
VALUES
    ('12312312', '00000003', 7, 'good job!!', 'Mr Professor', 0);
INSERT INTO Reviews
    (app_id, reviewer_id, ranking, comments, recommended_advisor, reject_reason)
VALUES
    ('66666666', '00000004', 2, 'bad job!!', 'The Doctor', 0);

-- PriorDegrees
INSERT INTO PriorDegrees
    (user_id, bachelors, bachelors_gpa, bachelors_major, bachelors_grad_year, bachelors_university, masters, masters_gpa, masters_major, masters_grad_year, masters_university)
VALUES
    ('12312312', 1, 4, 'Computer Science', 2044, 'George Washington University', 1, 4, 'Computer Science', 2046, 'the same one!');
INSERT INTO PriorDegrees
    (user_id, bachelors, bachelors_gpa, bachelors_major, bachelors_grad_year, bachelors_university, masters, masters_gpa, masters_major, masters_grad_year, masters_university)
VALUES
    ('66666666', 1, 2, 'Computer Science', 2031, 'George Washington University', 1, 3, 'Computer Science', 2033, 'a different one, idk');