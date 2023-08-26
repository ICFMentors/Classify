PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE user (
	"userID" INTEGER NOT NULL, 
	first_name VARCHAR(50) NOT NULL, 
	last_name VARCHAR(50) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	password VARCHAR(100) NOT NULL, 
	age INTEGER NOT NULL, 
	gender VARCHAR(10) NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	PRIMARY KEY ("userID"), 
	UNIQUE (email), 
	UNIQUE (username)
);
INSERT INTO user VALUES(1,'Hamza','Bandarkar','hamzabandarkar929@gmail.com','h123','bandarkar123',19,'1','student');
INSERT INTO user VALUES(2,'Yaseen','Khan','goyaseenkhan@gmail.com','ykhan','ykhan',15,'1','student');
INSERT INTO user VALUES(3,'Ibraheem','Khan','goibraheemkhan@gmail.com','ikhan','ikhan',16,'1','student');
INSERT INTO user VALUES(4,'Yusuf','Bandarkar','ybandarkar772@gmail.com','ybandarkar','ybandarkar',16,'1','student');
INSERT INTO user VALUES(5,'Hadi','Bagdadi','bagdadihadi@gmail.com','hbagdadi','hbagdadi',20,'1','student');
INSERT INTO user VALUES(6,'Yusuf','Vaid','yvaid@example.com','yvaid','yvaids123',40,'1','student');
INSERT INTO user VALUES(7,'Bilal','Makda','bilalmakdaus@gmail.com','bmakda','bmakda',19,'1','student');
INSERT INTO user VALUES(8,'Saaim','Bagdadi','saaim.bagdadi@gmail.com','sbagdadi','sbagdadi',15,'1','student');
CREATE TABLE IF NOT EXISTS "FAQ" (
	"faqID" INTEGER NOT NULL, 
	question VARCHAR(255) NOT NULL, 
	answer VARCHAR(255) NOT NULL, 
	PRIMARY KEY ("faqID")
);
INSERT INTO FAQ VALUES(1,'How do I register for classes?','Please visit the course catalog, to browse classes being held, and simply click register, to be added to that class roster.');
INSERT INTO FAQ VALUES(2,'How do I pay for classes?','Unfortunately, we have not yet implemented a way to pay for classes. But we plan to include that along with other functionalities in further updates.');
CREATE TABLE teacher (
	"teacherID" INTEGER NOT NULL, 
	qualifications VARCHAR(400) NOT NULL, 
	experience VARCHAR(400) NOT NULL, 
	department VARCHAR(255) NOT NULL, 
	status VARCHAR(255) NOT NULL, 
	"userID" INTEGER NOT NULL, 
	PRIMARY KEY ("teacherID"), 
	FOREIGN KEY("userID") REFERENCES user ("userID")
);
INSERT INTO teacher VALUES(1,'none','none','CS','teacher',1);
INSERT INTO teacher VALUES(2,'none','none','none','none',2);
INSERT INTO teacher VALUES(3,'','','','',3);
INSERT INTO teacher VALUES(4,'','','','',4);
INSERT INTO teacher VALUES(5,'','','','',5);
INSERT INTO teacher VALUES(6,'','','','',6);
CREATE TABLE parent (
	"parentID" INTEGER NOT NULL, 
	"student1ID" INTEGER NOT NULL, 
	"student2ID" INTEGER NOT NULL, 
	"student3ID" INTEGER NOT NULL, 
	"student4ID" INTEGER NOT NULL, 
	PRIMARY KEY ("parentID"), 
	FOREIGN KEY("student1ID") REFERENCES user ("userID"), 
	FOREIGN KEY("student2ID") REFERENCES user ("userID"), 
	FOREIGN KEY("student3ID") REFERENCES user ("userID"), 
	FOREIGN KEY("student4ID") REFERENCES user ("userID")
);
CREATE TABLE registration (
	user_id INTEGER NOT NULL, 
	course_id INTEGER NOT NULL, 
	PRIMARY KEY (user_id, course_id), 
	FOREIGN KEY(user_id) REFERENCES user ("userID"), 
	FOREIGN KEY(course_id) REFERENCES course ("courseID")
);
INSERT INTO registration VALUES(5,1);
INSERT INTO registration VALUES(1,1);
INSERT INTO registration VALUES(3,2);
INSERT INTO registration VALUES(3,1);
INSERT INTO registration VALUES(2,2);
INSERT INTO registration VALUES(1,2);
INSERT INTO registration VALUES(7,2);
INSERT INTO registration VALUES(8,2);
CREATE TABLE course (
	"courseID" INTEGER NOT NULL, 
	"courseName" VARCHAR(255) NOT NULL, 
	description VARCHAR(255) NOT NULL, 
	section VARCHAR(10) NOT NULL, 
	"totalSeats" INTEGER NOT NULL, 
	"seatsTaken" INTEGER NOT NULL, 
	"teacherID" INTEGER NOT NULL, 
	dates VARCHAR(255) NOT NULL, 
    days VARCHAR(255) NOT NULL,
	timings VARCHAR(255) NOT NULL,
    "active" INTEGER NOT NULL,
	PRIMARY KEY ("courseID"), 
	FOREIGN KEY("teacherID") REFERENCES teacher ("teacherID")
);
INSERT INTO course VALUES(1,'iOS Programming','iOS Programming','1',5,3,6,'TBD','TBD','TBD',1);
INSERT INTO course VALUES(2,'Cooking at Harvey Green!','Get cooked at Harvey Green by yours truly, Hadi Bagdadi!','1',15,5,5,'06-01-2021','Every Day','6:30PM - 8:30PM',1);
CREATE TABLE announcement (
    "announcementID" INTEGER NOT NULL, 
    "text" VARCHAR(255) NOT NULL, 
    "courseID" INTEGER NOT NULL, 
    "active" INTEGER,  -- Change to INTEGER instead of INTEGER NOT NULL
    "expiration_date" VARCHAR(55),  -- Use TEXT for storing datetime
    PRIMARY KEY ("announcementID"), 
    FOREIGN KEY ("courseID") REFERENCES course ("courseID")
);
INSERT INTO announcement VALUES(1,'Lets play at 6:15!',2,0,NULL);
INSERT INTO announcement VALUES(2,'Lets play at 6:30!',2,0,NULL);
INSERT INTO announcement VALUES(3,'Lets play today!',2,1,NULL);
CREATE TABLE IF NOT EXISTS "question" (
	"questionID" INTEGER NOT NULL, 
	query VARCHAR(500) NOT NULL, 
	answer VARCHAR(255), 
    "userID" INTEGER NOT NULL,
	PRIMARY KEY ("questionID"),
    FOREIGN KEY("userID") REFERENCES user ("userID")
);
COMMIT;
