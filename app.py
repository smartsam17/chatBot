from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
import pymongo
from flask_cors import CORS
from googlesearch import search 
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
auth = HTTPBasicAuth()
import requests
from bs4 import BeautifulSoup

myclient = pymongo.MongoClient("mongodb://sachin17:Sapple123!@ds125953.mlab.com:25953/homoeopathy_in_kanpur")
mydb = myclient["homoeopathy_in_kanpur"]
reviewsCol = mydb["reviews"]

def scrappingAmazon(productName):
    headers =  {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    query = productName +" product review in amazon"
    for j in search(query, num=10, stop=1, pause=1): 
        baseUrl = j     
    page = requests.get(baseUrl)
    soup = BeautifulSoup(page.text, 'html.parser')
    pageLength = soup.find(class_="a-section a-spacing-medium").find(class_="a-size-base").contents[0].split('of')
    recordsPerpage = int(pageLength[0].split('-')[1])
    totalrecords = int(pageLength[1].replace("reviews", "")) 
    nummerous =  totalrecords / int(recordsPerpage)
    denominator = totalrecords % int(recordsPerpage)
    if denominator >0:
        nummerous += 1
    totalPages = int(nummerous)    
    productTitle = soup.find(class_="product-title").find(class_="a-link-normal").contents[0]
    for i in range(1,totalPages):
        url = baseUrl+'?pageNumber='+str(i)
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        reviews = soup.find_all(class_="review")
        for reviewItem in reviews:
            title = reviewItem.find(class_='review-title').find(class_="").contents[0]
            description = reviewItem.find(class_='review-text-content').find(class_="").contents[0]
            ratingTitle = reviewItem.find(class_='review-rating').find(class_="a-icon-alt").contents[0]
            rating = int(ratingTitle.split('of')[1].replace('stars',''))
            data = {
                'source': 'Amazon',
                'product': productName.lower(),     
                'title': title,
                'rating': rating,
                'description': description
                }
            #print(data)    
            x = reviewsCol.insert_one(data)   
    return True

def scrappingFlipKart(productName):
    headers =  {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    query = productName +" product reviews in flipkart"
    for j in search(query, num=10, stop=1, pause=1): 
        baseUrl = j     
    print("URL===", baseUrl)    
    page = requests.get(baseUrl)
    soup = BeautifulSoup(page.text, 'html.parser')
    pageLength = soup.find(class_="_2zg3yZ _3KSYCY").find(class_="").contents[0].split("of ")
    for i in range(1,int(pageLength[1].replace(',', ''))):
        url = baseUrl+"&page="+str(i)
        page = requests.get(url, headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        reviewItems = soup.find_all(class_='col _390CkK _1gY8H-')
        for reviewItem in reviewItems:
            rating = reviewItem.find(class_="row").find_all('div')[0].contents[0]
            title = reviewItem.find(class_='_2xg6Ul').contents[0]
            description = reviewItem.find(class_='qwjRop').find(class_="").find(class_="").contents[0]
            data = {
            'source': 'Flipkart',    
            'product': productName.lower(),     
            'title': title,
            'rating': rating,
            'description': description
            }
            #print(data)
            x = reviewsCol.insert_one(data)
    return True        

@app.route('/api/v1.0/reviews', methods=['GET'])
def reviews():
    productName = request.args.get('productName')
    deleteQuery = { "product": productName }
    x = reviewsCol.delete_many(deleteQuery)
    scrappingAmazon(productName)
    scrappingFlipKart(productName)
    reviewList = []
    myquery = {"product": productName}
    for x in reviewsCol.find(myquery):
        record = {"source": x["source"],"product": x["product"], "title": x["title"], "rating": x["rating"], "description": x["description"]}
        reviewList.append(record)
    return jsonify({'reviewList': reviewList})    

@app.route('/api/v1.0/reviews', methods=['DELETE'])
def delete_review():
    productName = request.args.get('productName')
    deleteQuery = { "product": productName }
    x = reviewsCol.delete_many(deleteQuery)
    return jsonify({'mesage': 'Reviews deleted successfully.'})    


@app.route("/")
def index():
    return "Welcome..."


@app.route('/api/v1.0/products', methods=['GET'])
def allProducts():
    return jsonify({'productList': mydb.reviews.distinct( "product" )})    


@app.route('/api/v1.0/reviews1', methods=['GET'])
def reviews1():
    #mydb.reviews.remove({})
    productName = request.args.get('productName')
    reviewList = []
    myquery = {"product": productName.lower()}
    for x in reviewsCol.find(myquery):
        record = {"source": x["source"],"product": x["product"], "title": x["title"], "rating": x["rating"], "description": x["description"]}
        reviewList.append(record)
    return jsonify({'reviewList': reviewList})    

@app.route('/api/v1.0/reviews1', methods=['POST'])
def insertReview():
    productName = request.form.get('productName')
    scrappingFlipKart(productName)
    return jsonify({'message': "success"})    



if __name__ == "__main__":
    app.run(debug = True)




    
