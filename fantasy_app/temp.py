from flask import Flask, request, render_template, redirect, url_for
from espn_api.football import League
import sqlite3

app = Flask(__name__)

# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect('fantasy.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to fetch and store data if not in the database
def get_or_fetch_player_data(year, espn_s2, swid):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if player data for the given year already exists
    cursor.execute('SELECT * FROM players WHERE year = ?', (year,))
    data = cursor.fetchall()

    if data:
        # If data exists, return it
        players = [dict(row) for row in data]
    else:
        # If data doesn't exist, fetch from ESPN
        league = League(
            league_id="368212",  # Replace with actual league ID
            year=year,
            espn_s2=espn_s2,
            swid=swid
        )

        players = []
        for position in ["QB", "RB", "WR", "TE", "K", "D/ST"]:
            for player in league.free_agents(position=position)[:10]:
                players.append({
                    "year": year,
                    "position": position,
                    "name": player.name,
                    "team": player.proTeam,
                    "points": player.total_points
                })
                # Insert new player data into the database
                cursor.execute('''
                    INSERT OR IGNORE INTO players (year, position, name, team, points)
                    VALUES (?, ?, ?, ?, ?)
                ''', (year, position, player.name, player.proTeam, player.total_points))
        
        conn.commit()

    conn.close()
    return players

# Route to select year
@app.route('/select_year', methods=['GET', 'POST'])
def select_year():
    if request.method == 'POST':
        year = int(request.form['year'])
        return redirect(url_for('show_top_players', year=year))
    return render_template('select_year.html')

# Route to display top players for a specific year
@app.route('/top_players/<int:year>')
def show_top_players(year):
    # Retrieve credentials from the database
    conn = get_db_connection()
    credentials = conn.execute('SELECT * FROM credentials').fetchone()
    conn.close()

    if not credentials:
        return "Credentials not set. Please set them first.", 400

    # Retrieve data for the specified year, fetching from ESPN if not in the database
    players = get_or_fetch_player_data(year, credentials['espn_s2'], credentials['swid'])

    return render_template('players.html', players=players, year=year)

# Route to add or update credentials
@app.route('/set_credentials', methods=['GET', 'POST'])
def set_credentials():
    if request.method == 'POST':
        espn_s2 = request.form['espn_s2']
        swid = request.form['swid']
        year = int(request.form['year'])

        conn = get_db_connection()
        # Clear existing credentials and insert new ones
        conn.execute('DELETE FROM credentials')
        conn.execute(
            'INSERT INTO credentials (espn_s2, swid, year) VALUES (?, ?, ?)',
            (espn_s2, swid, year)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('select_year'))
    return render_template('set_credentials.html')

@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    try:
        conn = sqlite3.connect('fantasy.db')
        print("Opened database successfully")
        
        # Ensure the credentials table is created
        conn.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            espn_s2 TEXT,
            swid TEXT,
            year INTEGER
        )
        ''')
        
        # Ensure the players table is created
        conn.execute('''
            CREATE TABLE IF NOT EXISTS players (
                year INTEGER,
                position TEXT,
                name TEXT,
                team TEXT,
                points REAL,
                PRIMARY KEY (year, position, name)
            )
        ''')
        
        conn.close()  # Close the connection after setup

        # Begin the Flask Application
        app.run(host="0.0.0.0", port=2224)
        
    except Exception as e:
        print("App failed on boot:", e)



    # try:
    #     con = sql.connect('ff.db')
    #     print("Opened database successfully")
    #     # ensure that the table students is ready to be written to
    #     con.execute('''
    #     CREATE TABLE IF NOT EXISTS credentials (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         espn_s2 TEXT,
    #         swid TEXT,
    #         year INTEGER
    #         )
    #     ''')
    #     # Table for player data
    #     con.execute('''
    #         CREATE TABLE IF NOT EXISTS players (
    #             year INTEGER,
    #             position TEXT,
    #             name TEXT,
    #             team TEXT,
    #             points REAL,
    #             PRIMARY KEY (year, position, name)
    #         )
    #     ''')
        
    #     # conn.commit()
    #     # conn.close()

    #     # init_db()
    #     con.close()
    #     # begin Flask Application 
    #     app.run(host="0.0.0.0", port=2224)
    # except:
    #     print("App failed on boot")