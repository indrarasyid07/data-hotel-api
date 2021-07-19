from flask import Flask, jsonify, request
import mysql.connector

db = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database='data_hotel'
)
cursor = db.cursor()
app = Flask(__name__)

cursor.execute("SELECT hotel.*,review.review_id,review.judul,review.isi,review.tanggal_menginap,review.jenis_trip,review_rating,user.* FROM review INNER JOIN hotel ON review.hotel_id = hotel.hotel_id INNER JOIN user ON review.user_id = user.user_id")
data_scraping_gabungan = cursor.fetchall()
cursor.execute("SELECT * FROM hotel")
data_scraping_hotel = cursor.fetchall()
cursor.execute("SELECT * FROM user")
data_scraping_user = cursor.fetchall()
cursor.execute("SELECT * FROM review")
data_scraping_review = cursor.fetchall()

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>Data Tidak Ditemukan</p>", 404

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Data Review Hotel Tripadvisor</h1>'''

@app.route('/gabungan', methods=['GET'])
def api_gabungan():
    return jsonify(data_scraping_gabungan)
  
@app.route('/review', methods=['GET'])
def review():
  return jsonify(data_scraping_review)

@app.route('/review/<variable1>/<variable2>', methods=['GET'])
def review_filter(variable1,variable2):
  column_name = ["review_id", 'hotel_id', 'user_id', 'judul', 'isi', 'tanggal_menginap', 'jenis_trip', 'review_rating']
  index = column_name.index(variable1)
  if index==0 or index==1 or index==2 or index==7:
    variable2=int(variable2)
  review = [review for review in data_scraping_review if review[index] == variable2]
  if len(review) == 0:
    return page_not_found(404)
  return jsonify(review)

@app.route('/user', methods=['GET'])
def user():
  return jsonify(data_scraping_user)

@app.route('/user/<variable1>/<variable2>', methods=['GET'])
def user_filter(variable1,variable2):
  column_name = ['user_id','nama_user']
  index = column_name.index(variable1)
  if index==0:
    variable2=int(variable2)
  user = [user for user in data_scraping_user if user[index] == variable2]
  if len(user) == 0:
    return page_not_found(404)
  return jsonify(user)

@app.route('/hotel', methods=['GET'])
def hotel():
  return jsonify(data_scraping_hotel)

@app.route('/hotel/<variable1>/<variable2>', methods=['GET'])
def hotel_filter(variable1,variable2):
  column_name = ['hotel_id','nama_hotel','','','','','','','','hotel_rating']
  index = column_name.index(variable1)
  if index==0 or index==9:
    variable2=float(variable2)
  hotel = [hotel for hotel in data_scraping_hotel if hotel[index] == variable2]
  if len(hotel) == 0:
    return page_not_found(404)
  return jsonify(hotel)

if __name__ == '__main__':
    app.run(debug=True)