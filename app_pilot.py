"""
Minimal pilot study app — only game engine, user manager, and pilot routes.
No numpy, torch, tensorflow, or visualization dependencies.
"""
import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS

from src.gamification.game_engine import GameEngine
from src.database.user_manager import UserManager
from src.utils.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'pilot-secret-key-2024')
app.config['DEBUG'] = False

CORS(app)

config = Config()
user_manager = UserManager()
game_engine = GameEngine()

os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

@app.route('/')
def index():
    return redirect(url_for('pilot_register'))

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.now().isoformat()})

"""
PILOT STUDY ROUTES — add these to app.py
Handles: participant registration, pre-test, training, post-test, export
"""

# ── PASTE THESE IMPORTS AT TOP OF app.py (if not already there) ─────────────
# from datetime import datetime
# import csv, io

# ── PASTE THESE ROUTES INTO app.py BEFORE the if __name__ == '__main__' line ─


@app.route('/pilot/register', methods=['GET', 'POST'])
def pilot_register():
    """
    Participant self-registration.
    Creates account and records demographics in one step.
    """
    if request.method == 'POST':
        data = request.form

        # Create user account (username = their email or chosen ID)
        username   = data.get('participant_id').strip()
        email      = data.get('email', f"{username}@pilot.local").strip()
        password   = data.get('password', 'pilot2024').strip()

        result = user_manager.create_user(username, email, password, role='participant')

        if 'error' in result:
            return render_template('pilot_register.html',
                                   error=result['error'])

        user_id = result['user_id']

        # Save demographics to user profile
        demographics = {
            'age':              data.get('age'),
            'gender':           data.get('gender'),
            'education':        data.get('education'),
            'email_hours_day':  data.get('email_hours'),
            'prior_training':   data.get('prior_training'),
            'registered_at':    datetime.now().isoformat(),
            'session':          1
        }

        with __import__('sqlite3').connect(user_manager.db_path) as conn:
            conn.execute(
                "UPDATE users SET profile_data=? WHERE id=?",
                (__import__('json').dumps(demographics), user_id)
            )

        # Auto-login
        session['user_id']   = user_id
        session['username']  = username
        session['session_no'] = 1

        return redirect(url_for('pilot_pretest'))

    return render_template('pilot_register.html')


@app.route('/pilot/login', methods=['GET', 'POST'])
def pilot_login():
    """
    Returning participant login for Session 2.
    """
    if request.method == 'POST':
        username = request.form.get('participant_id').strip()
        password = request.form.get('password', 'pilot2024').strip()

        user = user_manager.authenticate_user(username, password)
        if 'error' in user:
            return render_template('pilot_login.html', error='ID not found. Check your participant ID.')

        session['user_id']   = user['user_id']
        session['username']  = username

        # Determine which session they are on
        import sqlite3, json as _json
        with sqlite3.connect(user_manager.db_path) as conn:
            row = conn.execute(
                "SELECT profile_data FROM users WHERE id=?",
                (user['user_id'],)
            ).fetchone()
            profile = _json.loads(row[0]) if row and row[0] else {}

        session_no = profile.get('session', 1)
        if session_no == 1:
            return redirect(url_for('pilot_pretest'))
        elif session_no == 2:
            return redirect(url_for('pilot_posttest'))
        else:
            return redirect(url_for('pilot_thankyou'))

    return render_template('pilot_login.html')


@app.route('/pilot/pretest')
def pilot_pretest():
    """Session 1 — Pre-test assessment (10 fixed questions, no feedback)."""
    if 'user_id' not in session:
        return redirect(url_for('pilot_login'))

    questions = game_engine.get_assessment_questions()
    return render_template('pilot_assessment.html',
                           questions=questions,
                           assessment_type='pre',
                           title='Pre-Training Assessment',
                           instructions=(
                               'For each item below, decide: Is this phishing or legitimate? '
                               'Answer based on your current knowledge. '
                               'No hints — do your best.'
                           ))


@app.route('/pilot/training')
def pilot_training():
    """Session 1 — Training games (after pre-test)."""
    if 'user_id' not in session:
        return redirect(url_for('pilot_login'))

    user_id = session['user_id']
    available = game_engine.get_available_games(user_id)
    return render_template('pilot_training.html', games=available)


@app.route('/pilot/posttest')
def pilot_posttest():
    """Session 2 — Post-test assessment (same 10 questions)."""
    if 'user_id' not in session:
        return redirect(url_for('pilot_login'))

    questions = game_engine.get_assessment_questions()
    return render_template('pilot_assessment.html',
                           questions=questions,
                           assessment_type='post',
                           title='Post-Training Assessment',
                           instructions=(
                               'Same task as last week — decide whether each item is '
                               'phishing or legitimate. Answer based on what you know now.'
                           ))


@app.route('/api/pilot/submit_assessment', methods=['POST'])
def submit_assessment():
    """
    Save pre-test or post-test results.
    Receives: {assessment_type: 'pre'/'post', answers: [...], time_taken_ms: [...]}
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data        = request.get_json()
    user_id     = session['user_id']
    atype       = data.get('assessment_type', 'pre')   # 'pre' or 'post'
    answers     = data.get('answers', [])               # [{challenge_id, user_answer, time_ms}]
    started_at  = data.get('started_at', datetime.now().isoformat())

    # Score answers
    correct = 0
    detailed = []
    questions = game_engine.get_assessment_questions()
    q_map = {q['id']: q for q in questions}

    for ans in answers:
        cid          = ans.get('challenge_id')
        user_answer  = ans.get('user_answer')
        time_ms      = ans.get('time_ms', 0)
        q            = q_map.get(cid, {})
        is_correct   = user_answer == q.get('correct_answer')
        if is_correct:
            correct += 1
        detailed.append({
            'challenge_id': cid,
            'user_answer':  user_answer,
            'correct':      is_correct,
            'time_ms':      time_ms
        })

    score    = correct
    accuracy = round(correct / len(questions) * 100, 1) if questions else 0

    # Persist to game_sessions table
    import json as _json
    game_type_label = f'{atype}_assessment'
    user_manager.log_game_session(
        user_id    = user_id,
        game_id    = f"{user_id}_{atype}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        game_type  = game_type_label,
        score      = score,
        answers    = detailed,
        completed  = True
    )

    # Update session marker in profile_data
    import sqlite3
    with sqlite3.connect(user_manager.db_path) as conn:
        row = conn.execute(
            "SELECT profile_data FROM users WHERE id=?", (user_id,)
        ).fetchone()
        profile = _json.loads(row[0]) if row and row[0] else {}

        if atype == 'pre':
            profile['session'] = 2
            profile['pre_completed_at'] = datetime.now().isoformat()
        elif atype == 'post':
            profile['session'] = 3
            profile['post_completed_at'] = datetime.now().isoformat()

        conn.execute(
            "UPDATE users SET profile_data=? WHERE id=?",
            (_json.dumps(profile), user_id)
        )

    response = {
        'score':         score,
        'total':         len(questions),
        'accuracy':      accuracy,
        'correct':       correct,
        'assessment_type': atype,
        'next_url': url_for('pilot_training') if atype == 'pre' else url_for('pilot_thankyou')
    }
    return jsonify(response)


@app.route('/pilot/thankyou')
def pilot_thankyou():
    """Thank-you page shown after Session 2 post-test."""
    return render_template('pilot_thankyou.html')


# ── RESEARCHER EXPORT ROUTE ──────────────────────────────────────────────────

@app.route('/admin/export_pilot')
def export_pilot_data():
    """
    Download all pilot study results as CSV.
    Open this URL in your browser:  https://your-app.onrender.com/admin/export_pilot
    Protected by simple query-param token — change 'phd2024' to something private.
    """
    token = request.args.get('token', '')
    if token != os.environ.get('EXPORT_TOKEN', 'phd2024'):
        return "Forbidden", 403

    import sqlite3, csv, io, json as _json

    conn = sqlite3.connect(user_manager.db_path)

    # Get all users with profile data
    users = conn.execute("""
        SELECT u.id, u.username, u.profile_data,
               pre.score  AS pre_score,
               pre.answers AS pre_answers,
               post.score AS post_score,
               post.answers AS post_answers
        FROM users u
        LEFT JOIN (
            SELECT user_id, score, answers
            FROM game_sessions WHERE game_type='pre_assessment'
        ) pre  ON pre.user_id  = u.id
        LEFT JOIN (
            SELECT user_id, score, answers
            FROM game_sessions WHERE game_type='post_assessment'
        ) post ON post.user_id = u.id
        WHERE u.role = 'participant'
    """).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'participant_id', 'username', 'age', 'gender', 'education',
        'email_hours_day', 'prior_training', 'registered_at',
        'pre_score', 'pre_accuracy_%',
        'post_score', 'post_accuracy_%',
        'improvement_score', 'improvement_%',
        'completed_both_sessions'
    ])

    total_questions = len(game_engine.get_assessment_questions())

    for row in users:
        uid, uname, profile_raw, pre_s, pre_a, post_s, post_a = row
        profile = _json.loads(profile_raw) if profile_raw else {}

        pre_score  = pre_s  if pre_s  is not None else ''
        post_score = post_s if post_s is not None else ''

        pre_acc  = round(pre_score  / total_questions * 100, 1) if pre_score  != '' else ''
        post_acc = round(post_score / total_questions * 100, 1) if post_score != '' else ''

        improvement = (post_score - pre_score) if (pre_score != '' and post_score != '') else ''
        imp_pct     = round((improvement / total_questions) * 100, 1) if improvement != '' else ''
        completed   = 'Yes' if (pre_score != '' and post_score != '') else 'No'

        writer.writerow([
            uid, uname,
            profile.get('age',''), profile.get('gender',''),
            profile.get('education',''), profile.get('email_hours_day',''),
            profile.get('prior_training',''), profile.get('registered_at',''),
            pre_score,  pre_acc,
            post_score, post_acc,
            improvement, imp_pct,
            completed
        ])

    conn.close()
    output.seek(0)

    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=pilot_results.csv'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
