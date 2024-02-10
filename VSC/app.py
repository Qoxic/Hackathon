from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import math
import folium
import ast

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

class RegistrationForm:
    def __init__(self, username, password, confirm_password):
        self.username = username
        self.password = password
        self.confirm_password = confirm_password

@login_manager.user_loader
def load_user(user_id):
    # This should be adjusted to match how users are actually loaded based on `user_id`
    return User(user_id)


# In-memory "database" for demonstration purposes
offers = []
requests = []


    
@app.route('/')
def index():
    return '''
    <h1>Welcome to Linck Click</h1> \
    <br><button onclick="location.href='/offer_help'">Offer Help</button>
    <br><button onclick="location.href='/request_help'">Request Help</button>
    <br><button onclick="location.href='/login'">Login to map</button>
    <br><button onclick="location.href='/matched'">Matched</button>
    <br><button onclick="location.href='/number_checked'">Number query</button>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        Payment_info = request.form['card_number']

        if not username or not password or not confirm_password:
            flash('Please fill out all fields.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match.', 'danger')
        else:
            with open('users.txt', 'a+') as users_file:
                users_file.seek(0)
                users = [line.split(',')[0] for line in users_file.readlines()]
                if username in users:
                    flash('Username already exists.', 'danger')
                else:
                    users_file.write(f'{username},{password}\n')
                    flash('Account created successfully. You can now log in.', 'success')
                    return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open('users.txt', 'r') as users_file:
            for line in users_file:
                stored_username, stored_password = line.strip().split(',')
                if stored_username == username and stored_password == password:
                    return redirect(url_for('show_map'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/map')
def show_map():
    # Load offer data from the "database"
    offer_data = []
    try:
        with open('offers.txt', 'r') as offer_file:
            offer_lines = offer_file.readlines()
            for line in offer_lines:
                entry = ast.literal_eval(line)
                offer_data.append(entry)
    except FileNotFoundError:
        pass

    # Load request data from the "database"
    request_data = []
    try:
        with open('requests.txt', 'r') as request_file:
            request_lines = request_file.readlines()
            for line in request_lines:
                entry = ast.literal_eval(line)
                request_data.append(entry)
    except FileNotFoundError:
        pass

    # Create a map
    map_object = folium.Map(location=[51.5074, -0.1278], zoom_start=10)

    # Add pins for each offer entry in the data
    for offer_entry in offer_data:
        name = offer_entry['name']
        number = offer_entry['number']
        longitude = float(offer_entry['longitude'])
        latitude = float(offer_entry['latitude'])
        popup_text = f"Name: {name}<br>Number: {number}"

        folium.Marker(
            location=[latitude, longitude],
            popup=popup_text,
            icon=folium.Icon(color='blue')
        ).add_to(map_object)

    # Add pins for each request entry in the data (displayed in red) with clickable popups
    for request_entry in request_data:
        name = request_entry['name']
        number = request_entry['number']
        resources = request_entry['resources']
        skills = request_entry['skills']
        longitude = float(request_entry['longitude'])
        latitude = float(request_entry['latitude'])
        popup_text = f"Name: {name}<br>Number: {number}<br>Resources: {resources}<br>Skills: {skills}"

        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color='red')
        ).add_to(map_object)

    # Save the map
    map_object.save('templates/map.html')

    # Render the HTML template with the map
    return render_template('map.html')


@app.route('/offer_help', methods=['GET', 'POST'])
def offer_help():
    if request.method == 'POST':
        # Extract data from the form submission
        offerfile = open("offers.txt","a")
        name = request.form.get('name')
        number = request.form.get('number')
        skills = request.form.get('skills')
        resources = request.form.get('resources')
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        # Append the data to the "database"
        offers.append({
            'name': name,
            'number': number,
            'skills': skills,
            'resources': resources,
            'longitude': longitude,
            'latitude': latitude
        })
        
        for item in offers:
            # Convert the dictionary to a string representation
            dict_string = str(item)
            # Write the string to the file
            offerfile.write(dict_string + '\n')

        
        offerfile.close()
        # Redirect to a thank you page or back to the form
        return redirect(url_for('thank_you'))
    else:
        # Render the offer help form when method is GET
        return render_template('offer_help.html')


@app.route('/thank_you')
def thank_you():
    # A simple thank you page after submission
    return '<h2>Thank you!</h2><a href = "/">Back to Home<a>'

@app.route('/request_help', methods=['GET', 'POST'])
def request_help():
    if request.method == 'POST':
        requestfile = open("requests.txt","a")
        name = request.form.get('name')
        number = request.form.get('number')
        arange = request.form.get('arange')
        skills = request.form.get('skills')
        resources = request.form.get('resources')
        longitude = request.form.get('longitude')
        latitude = request.form.get('latitude')
        
        # Append the data to the "database"
        requests.append({
            'name': name,
            'number': number,
            'skills': skills,
            'resources': resources,
            'longitude': longitude,
            'latitude': latitude,
            'arange': arange
        })

        for item in requests:
            # Convert the dictionary to a string representation
            dict_string = str(item)
            # Write the string to the file
            requestfile.write(dict_string + '\n')
        requestfile.close()
        # Redirect to a thank you page or back to the form
        return redirect(url_for('thank_you'))
    else:
        # Render the offer help form when method is GET
        return render_template('request_help.html')

#matching requests with 
def range_check(req_longitude,req_latitude,off_longitude,off_latitude,radius):
     # Convert decimal degrees to radians
    req_longitude, req_latitude, off_longitude, off_latitude = map(math.radians, [req_longitude, req_latitude, off_longitude, off_latitude])

    # Haversine formula
    dlon = off_longitude - req_longitude
    dlat = off_latitude - req_latitude
    a = math.sin(dlat / 2) ** 2 + math.cos(req_latitude) * math.cos(off_latitude) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Radius of earth in kilometers is 6371
    distance = 6371 * c
    if distance <= radius:
        return True
    else:
        return False
    
def get_matched():
    matched_requests = []  # List to store matched requests
    offerfile = open("offers.txt", "r")
    requestfile = open("requests.txt", "r")
    requestslist = requestfile.readlines()
    offerslist = offerfile.readlines()
    
    for req_line in requestslist:
        a = eval(req_line)
        req_skill = a['skills']
        req_res = a['resources']
        arange = a['arange']
        
        for off_line in offerslist:
            b = eval(off_line)
            off_skill = b['skills']
            off_res = b['resources']
            
            if req_skill == off_skill or req_res == off_res:
                if range_check(float(a['longitude']), float(a['latitude']), float(b['longitude']), float(b['latitude']),int(arange)):
                    matched_requests.append((a, b))  # Append matched request-offer pair to the list
    
    offerfile.close()
    requestfile.close()
    return matched_requests

@app.route('/matched', methods=['GET', 'POST'])
def matching():

    matching_requests = get_matched()
    if matching_requests:
        return render_template('matched.html', matched=True, matched_requests=matching_requests)
    else:
        return render_template('matched.html', matched=False)


@app.route('/number_checked', methods=['GET', 'POST'])
def number_check():
    if request.method == 'POST':

        return redirect(url_for('number_checked_res'))
    else:
        # Render the offer help form when method is GET
        return render_template('number_checked.html')
    
@app.route('/number_checked_res', methods=['GET', 'POST'])
def number_check_res():
    if request.method == 'POST':
        matched_list = []
        number = request.form.get('number')
        matched_request = get_matched()
        print("hi")
        for (a,b) in matched_request:
            if number == a['number']:
                matched_list.append((a,b))
            if number == b['number']:
                matched_list.append((a,b))
        print("Matched_list=", matched_list)
        if matched_list:
            return render_template('number_checked_res.html', matched=True, matched_requests=matched_list)
        else:
            return render_template('number_checked_res.html', matched=False)

if __name__ == '__main__':
    app.run(host='172.20.86.127', port=5000, debug=True)