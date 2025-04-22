from flask import Flask, request, render_template, redirect, session, url_for
import sqlite3, random

app = Flask('app')
app.secret_key = "superSecretPassword"



def connect_db():
    connection = sqlite3.connect('apps.db')
    connection.row_factory = sqlite3.Row
    return connection


def generate_user_id():
    while True:
        user_id = random.randint(10000000, 99999999)
        db = connect_db()
        cursor = db.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))

        if not cursor.fetchone():
            return user_id


@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    db = connect_db()
    cursor = db.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    if user is None:
        session.clear()
        return redirect('/login')

    if user['role'] == 'Applicant':
        return redirect('/applicant/dashboard')
    
    elif user['role'] == 'GS':
        return redirect('/gs/dashboard')
    
    elif user['role'] == 'CAC':
        return redirect('/cac/dashboard')
    
    elif user['role'] == 'Reviewer':
        return redirect('/reviewer/dashboard')
    
    return 'Unknown role'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        errorMessage = False

        db = connect_db()
        cursor = db.execute('SELECT * FROM Users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()

        if user is not None:
            session['user_id'] = user['user_id']
            return redirect('/')
        else:
            errorMessage = True
            return render_template('login.html', errorMessage=errorMessage)
    return render_template('login.html')


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_id = generate_user_id()
        role = 'Applicant'


        errorMessage1 = False
        errorMessage2 = False

        if not username or not password:
            errorMessage1 = True
            return render_template('signUp.html', errorMessage1=errorMessage1, errorMessage2=errorMessage2)

        connection = connect_db()
        try:
            connection.execute(
                'INSERT INTO Users (user_id, username, password, role) VALUES (?, ?, ?, ?)', (user_id, username, password, role)
            )
            connection.commit()
        except sqlite3.IntegrityError:
            errorMessage2 = True
            return render_template('signUp.html', errorMessage1=errorMessage1, errorMessage2=errorMessage2)
        finally:
            connection.close()

        return redirect(url_for('login'))

    return render_template('signUp.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/reset', methods=['POST'])
def reset_database():
    
    db = connect_db()
    try:
        # Clear existing records
        db.executescript('''
            DELETE FROM FinalDecisions;
            DELETE FROM Reviews;
            DELETE FROM RecommendationLetters;
            DELETE FROM PriorDegrees;
            DELETE FROM Applicants;
            DELETE FROM PersonalInfo;
            DELETE FROM Users;
        ''')

        # Repopulate
        db.executescript('''
            -- Users: Applicants
            INSERT INTO Users (user_id, username, password, role)
            VALUES ('12312312', 'John', 'JohnLennon123', 'Applicant');
            INSERT INTO Users (user_id, username, password, role)
            VALUES ('66666666', 'Ringo', 'RingoStarr123', 'Applicant');

            -- Personal Info
            INSERT INTO PersonalInfo (ssn, fname, lname, address, phone, email)
            VALUES ('111-11-1111', 'John', 'Lennon', '1234 Address Lane', '202-303-4040', 'jlennon25@gmail.com');
            INSERT INTO PersonalInfo (ssn, fname, lname, address, phone, email)
            VALUES ('222-11-1111', 'Ringo', 'Starr', '5678 Address Lane', '505-606-7070', 'rstarr25@gmail.com');

            -- Users: Faculty
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
        ''')

        db.commit()
    except Exception as e:
        return f"Error resetting database: {e}", 500
    finally:
        db.close()
    
    return redirect('/')



#-------------------- DASHBOARD ROUTES -----------------------#


@app.route('/gs/dashboard')
def gs_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    db = connect_db()
    applicants = db.execute('''
        SELECT a.app_id, pi.fname, pi.lname, pi.email, a.application_status
        FROM Applicants a
        JOIN PersonalInfo pi ON a.ssn = pi.ssn
    ''').fetchall()

    return render_template('gs_dashboard.html', applicants=applicants)


@app.route('/applicant/dashboard')
def applicant_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    db = connect_db()

    application = db.execute(
        'SELECT * FROM Applicants WHERE app_id = ?', (user_id,)
    ).fetchone()

    application_exists = application is not None

    return render_template('applicant_dashboard.html', application_exists=application_exists)


@app.route('/cac/dashboard')
def cac_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    db = connect_db()
    applicants = db.execute('''
        SELECT a.app_id, pi.fname, pi.lname, pi.email
        FROM Applicants a
        JOIN PersonalInfo pi ON a.ssn = pi.ssn
    ''').fetchall()

    return render_template('cac_dashboard.html', applicants=applicants)


@app.route('/reviewer/dashboard')
def reviewer_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    db = connect_db()
    applicants = db.execute('''
        SELECT a.app_id, pi.fname, pi.lname, pi.email
        FROM Applicants a
        JOIN PersonalInfo pi ON a.ssn = pi.ssn
    ''').fetchall()

    return render_template('reviewer_dashboard.html', applicants=applicants)



#-------------------- APPLICANT ROUTES -----------------------#


@app.route('/application/personal', methods=['GET', 'POST'])
def personal_application():

    if 'user_id' not in session:
        return redirect('/login')


    if request.method == 'POST':

        fname = request.form['fname']
        lname = request.form['lname']
        ssn = request.form['ssn']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']


        db = connect_db()
        db.execute('INSERT INTO PersonalInfo (fname, lname, ssn, address, phone, email) VALUES (?, ?, ?, ?, ?, ?)',
                   (fname, lname, ssn, address, phone, email))
        db.commit()
        return redirect('/applicant/dashboard')
    return render_template('applicant_personal.html')


@app.route('/application/new', methods=['GET', 'POST'])
def new_application():

    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']

    if request.method == 'POST':

        fname = request.form['fname']
        lname = request.form['lname']
        ssn = request.form['ssn']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        errorMessage = False

        degree_sought = request.form['degree_sought']
        admission_term = request.form['admission_term']
        admission_year = request.form['admission_year']
        gre_verbal = request.form['gre_verbal']
        gre_quantitative = request.form['gre_quantitative']
        gre_subject = request.form['gre_subject']
        work_experience = request.form['work_experience']

        bachelors = request.form.get('bachelors', 0)
        bachelors_gpa = request.form['bachelors_gpa']
        bachelors_major = request.form['bachelors_major']
        bachelors_year = request.form['bachelors_grad_year']
        bachelors_university = request.form['bachelors_university']
        masters = request.form.get('masters', 0)
        masters_gpa = request.form['masters_gpa']
        masters_major = request.form['masters_major']
        masters_year = request.form['masters_grad_year']
        masters_university = request.form['masters_university']
        
        recommender_name = request.form['recommender_name']
        recommender_email = request.form['recommender_email']
        recommender_title = request.form['recommender_title']
        recommender_affiliation = request.form['recommender_affiliation']

        db = connect_db()
        try:
            db.execute('INSERT INTO PersonalInfo (fname, lname, ssn, address, phone, email) VALUES (?, ?, ?, ?, ?, ?)',
                       (fname, lname, ssn, address, phone, email))
            db.commit()
        except sqlite3.IntegrityError:
            errorMessage = True
            return render_template('application.html', errorMessage=errorMessage)
        finally:
            db.close()


        db = connect_db()
        db.execute('INSERT INTO Applicants (app_id, ssn, degree_sought, admission_term, admission_year, gre_verbal, gre_quantitative, gre_subject, work_experience, application_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (user_id, ssn, degree_sought, admission_term, admission_year, gre_verbal, gre_quantitative, gre_subject, work_experience, 'Application Complete and Under Review/No Decision Yet'))
        db.commit()

        db = connect_db()
        db.execute('INSERT INTO PriorDegrees (user_id, bachelors, bachelors_gpa, bachelors_major, bachelors_grad_year, bachelors_university, masters, masters_gpa, masters_major, masters_grad_year, masters_university) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (user_id, bachelors, bachelors_gpa, bachelors_major, bachelors_year, bachelors_university, masters, masters_gpa, masters_major, masters_year, masters_university))
        db.commit()

        db = connect_db()
        db.execute('INSERT INTO RecommendationLetters (user_id, recommender_name, email, title, affiliation) VALUES (?, ?, ?, ?, ?)',
                   (user_id, recommender_name, recommender_email, recommender_title, recommender_affiliation))
        db.commit()

        return redirect('/applicant/dashboard')
    return render_template('application.html')


@app.route('/application/status')
def check_status():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    db = connect_db()


    application = db.execute('''
        SELECT a.*, p.fname, p.lname FROM Applicants a
        JOIN PersonalInfo p ON a.ssn = p.ssn
        WHERE a.app_id = ?
    ''', (user_id,)).fetchone()

    final_decision = db.execute('SELECT decision FROM FinalDecisions WHERE user_id = ?', (user_id,)).fetchone()

    if final_decision:
        if final_decision['decision'] == 'Admit':
            application = dict(application)
            application['application_status'] = 'Congratulations you have been admitted. The formal letter of acceptance will be mailed'
        elif final_decision['decision'] == 'Reject':
            application = dict(application)
            application['application_status'] = 'Your application for admission has been denied'

    return render_template('status.html', application=application)




#-------------------- GS ROUTES -----------------------#


@app.route('/gs/update_status/<string:app_id>', methods=['GET', 'POST'])
def update_status(app_id):
    if 'user_id' not in session:
        return redirect('/login')

    db = connect_db()

    if request.method == 'POST':
        new_status = request.form['status']
        reason = request.form.get('reason', '').strip()
        
        full_status = new_status
        if new_status == 'Application Incomplete' and reason:
            full_status += f" - Missing: {reason}"

        db.execute('UPDATE Applicants SET application_status = ? WHERE app_id = ?', (full_status, app_id))
        db.commit()
        return redirect('/')

    applicant = db.execute('''
        SELECT a.app_id, pi.fname, pi.lname
        FROM Applicants a
        JOIN PersonalInfo pi ON a.ssn = pi.ssn
        WHERE a.app_id = ?
    ''', (app_id,)).fetchone()
    return render_template('update_status.html', applicant=applicant)



"""
@app.route('/submit_recommendation/<int:app_id>', methods=['GET', 'POST'])
def submit_recommendation(app_id):

    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']

    if request.method == 'POST':
        db = connect_db()
        db.execute('UPDATE recommendations SET submitted = 1 WHERE application_id = ?', (app_id,))
        db.commit()
        return 'Recommendation submitted'
    return render_template('submit_recommendation.html')
"""


#-------------------- REVIEWER ROUTES -----------------------#


@app.route('/review/<string:app_id>', methods=['GET', 'POST'])
def review_applicant(app_id):
    if 'user_id' not in session:
        return redirect('/login')

    reviewer_id = session['user_id']
    db = connect_db()

    if request.method == 'POST':
        ranking = request.form['ranking']
        comments = request.form['comments']
        advisor = request.form['advisor']
        reject_reason = request.form.get('reject_reason')

        db.execute('''
            INSERT OR REPLACE INTO Reviews (app_id, reviewer_id, ranking, comments, recommended_advisor, reject_reason)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (app_id, reviewer_id, ranking, comments, advisor, reject_reason))
        db.commit()
        return redirect('/')

    # Fetch existing review if it exists
    review = db.execute('''
        SELECT * FROM Reviews WHERE app_id = ? AND reviewer_id = ?
    ''', (app_id, reviewer_id)).fetchone()

    # Join Applicants with PersonalInfo to get full applicant info
    applicant = db.execute('''
        SELECT a.*, p.fname, p.lname FROM Applicants a
        JOIN PersonalInfo p ON a.ssn = p.ssn
        WHERE a.app_id = ?
    ''', (app_id,)).fetchone()

    return render_template('review_form.html', applicant=applicant, review=review)




#-------------------- CAC ROUTES -----------------------#


@app.route('/cac/final_decision/<string:app_id>', methods=['POST'])
def cac_final_decision(app_id):
    if 'user_id' not in session:
        return redirect('/login')

    decision = request.form['decision']  # 'Admit' or 'Reject'
    decided_by = session['user_id']

    db = connect_db()
    # Save final decision
    db.execute('''
        INSERT OR REPLACE INTO FinalDecisions (user_id, decided_by, decision)
        VALUES (?, ?, ?)
    ''', (app_id, decided_by, decision))
    
    # Update application status
    db.execute('''
        UPDATE Applicants SET application_status = ?
        WHERE app_id = ?
    ''', (decision, app_id))

    db.commit()
    return redirect('/')



#-------------------- CAC ROUTES (CAC & Reviewer) -----------------------#


@app.route('/review/application/<string:app_id>')
def view_application(app_id):
    if 'user_id' not in session:
        return redirect('/login')

    # Optional: Check that this user is a reviewer or CAC
    db = connect_db()
    user = db.execute('SELECT * FROM Users WHERE user_id = ?', (session['user_id'],)).fetchone()
    if user['role'] not in ['Reviewer', 'CAC']:
        return render_template('error.html')

    # Fetch applicant personal and academic info
    applicant = db.execute('''
        SELECT a.*, pi.fname, pi.lname, pi.email, pi.address, pi.phone
        FROM Applicants a
        JOIN PersonalInfo pi ON a.ssn = pi.ssn
        WHERE a.app_id = ?
    ''', (app_id,)).fetchone()

    prior_degrees = db.execute('SELECT * FROM PriorDegrees WHERE user_id = ?', (app_id,)).fetchone()
    recommendations = db.execute('SELECT * FROM RecommendationLetters WHERE user_id = ?', (app_id,)).fetchall()
    reviews = db.execute('SELECT * FROM Reviews WHERE app_id = ?', (app_id,)).fetchall()
    

    return render_template('view_application.html', applicant=applicant, prior_degrees=prior_degrees, recommendations=recommendations, reviews=reviews)



app.run(host='0.0.0.0', port=8080)