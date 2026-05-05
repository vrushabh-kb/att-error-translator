from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import random
import string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)
CORS(app)

SENDGRID_API_KEY = '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'
SENDER_EMAIL = 'errortranslator.att@gmail.com'

def get_db():
    return mysql.connector.connect(
        host     = "tramway.proxy.rlwy.net",
        user     = "root",
        password = "qZiqtXricNLyVSggWCbnOZsHereDKCYI",
        database = "railway",
        port     = 17487
    )

# ── GET all error codes ──
@app.route('/api/errors', methods=['GET'])
def get_errors():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM error_codes")
    result = cursor.fetchall()
    db.close()
    return jsonify(result)

# ── POST add new error code ──
@app.route('/api/errors', methods=['POST'])
def add_error():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO error_codes (error_no, display_message) VALUES (%s, %s)",
                       (data['error_no'], data['display_message']))
        db.commit()
        db.close()
        return jsonify({"message": "Error code added successfully"}), 201
    except Exception as e:
        db.close()
        return jsonify({"message": "Duplicate error code! This error number already exists."}), 400

# ── PUT update error code ──
@app.route('/api/errors/<error_no>', methods=['PUT'])
def update_error(error_no):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE error_codes SET display_message=%s, updated_by=%s WHERE error_no=%s",
                   (data['display_message'], data['updated_by'], error_no))
    db.commit()
    db.close()
    return jsonify({"message": "Updated successfully"})

# ── DELETE error code ──
@app.route('/api/errors/<error_no>', methods=['DELETE'])
def delete_error(error_no):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM error_codes WHERE error_no=%s", (error_no,))
    db.commit()
    db.close()
    return jsonify({"message": "Deleted successfully"})

# ── LOGIN ──
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                   (data['username'], data['password']))
    user = cursor.fetchone()
    db.close()
    if user:
        return jsonify({
            "message": "Login successful",
            "username": user['username'],
            "iwrite": user['iwrite']
        })
    else:
        return jsonify({"message": "Invalid username or password"}), 401

# ── CHANGE PASSWORD ──
@app.route('/api/change-password', methods=['POST'])
def change_password():
    data = request.json
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                   (data['username'], data['old_password']))
    user = cursor.fetchone()
    if not user:
        db.close()
        return jsonify({"message": "Current password is incorrect"}), 401
    cursor2 = db.cursor()
    cursor2.execute("UPDATE users SET password=%s WHERE username=%s",
                    (data['new_password'], data['username']))
    db.commit()
    db.close()
    return jsonify({"message": "Password changed successfully"})

# ── PUBLIC LOOKUP ──
@app.route('/api/lookup/<error_no>', methods=['GET'])
def lookup_error(error_no):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT error_no, display_message FROM error_codes WHERE error_no=%s", (error_no,))
    result = cursor.fetchone()
    if result:
        cursor2 = db.cursor()
        cursor2.execute("INSERT INTO error_lookup_log (error_no) VALUES (%s)", (error_no,))
        db.commit()
    db.close()
    if result:
        return jsonify(result)
    else:
        return jsonify({"message": "Error code not found"}), 404

# ── ANALYTICS ──
@app.route('/api/analytics', methods=['GET'])
def analytics():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.error_no, e.display_message,
               COUNT(l.id) as lookup_count
        FROM error_codes e
        LEFT JOIN error_lookup_log l ON e.error_no = l.error_no
        GROUP BY e.error_no, e.display_message
        ORDER BY lookup_count DESC
    """)
    result = cursor.fetchall()
    db.close()
    return jsonify(result)

# ── REGISTER NEW USER + SEND EMAIL ──
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # check if username already exists
    cursor.execute("SELECT * FROM users WHERE username=%s", (data['username'],))
    existing = cursor.fetchone()
    if existing:
        db.close()
        return jsonify({"message": "Username already exists!"}), 400

    # insert new user
    cursor2 = db.cursor()
    cursor2.execute(
        "INSERT INTO users (username, password, iwrite, created_by) VALUES (%s, %s, %s, %s)",
        (data['username'], data['password'], data['iwrite'], data['created_by'])
    )
    db.commit()
    db.close()

    # send welcome email
    try:
        access_type = "Write Access (Admin)" if data['iwrite'] == 1 else "Read Only"
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=data['email'],
            subject='Welcome to AT&T Error Translator',
            plain_text_content=f"""Hello {data['username']},

Your account has been created on the AT&T Error Translator Admin Panel.

Your login details:
Username : {data['username']}
Password : {data['password']}
Access   : {access_type}

Please login at: https://charming-gaufre-4a3a5d.netlify.app
Change your password after first login.

Regards,
AT&T Error Translator Team"""
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent! Status: {response.status_code}")
        return jsonify({"message": "User registered and email sent successfully!"}), 201
    except Exception as e:
        print(f"EMAIL ERROR: {str(e)}")
        return jsonify({"message": "User created but email failed: " + str(e)}), 201

# ── FORGOT PASSWORD ──
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # check if username exists
    cursor.execute("SELECT * FROM users WHERE username=%s", (data['username'],))
    user = cursor.fetchone()
    if not user:
        db.close()
        return jsonify({"message": "Username not found!"}), 404

    # generate random temp password
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    # update password in db
    cursor2 = db.cursor()
    cursor2.execute("UPDATE users SET password=%s WHERE username=%s",
                    (temp_password, data['username']))
    db.commit()
    db.close()

    # send email with temp password
    try:
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=data['email'],
            subject='AT&T Error Translator — Password Reset',
            plain_text_content=f"""Hello {data['username']},

A password reset was requested for your account.

Your temporary password is: {temp_password}

Please login with this password and change it immediately.

If you did not request this, contact your administrator.

Regards,
AT&T Error Translator Team"""
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Reset email sent! Status: {response.status_code}")
        return jsonify({"message": "Temporary password sent to your email!"}), 200
    except Exception as e:
        print(f"EMAIL ERROR: {str(e)}")
        return jsonify({"message": "Password reset but email failed: " + str(e)}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)