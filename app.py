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
    data=[]
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
            data.append({
                'source': 'Amazon',
                'product': productName.lower(),     
                'title': title,
                'rating': rating,
                'description': description
                })
            #print(data)    
    x = reviewsCol.insert_many(data)   
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
    data=[]
    for i in range(1,int(pageLength[1].replace(',', ''))):
        url = baseUrl+"&page="+str(i)
        page = requests.get(url, headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        reviewItems = soup.find_all(class_='col _390CkK _1gY8H-')
        for reviewItem in reviewItems:
            rating = reviewItem.find(class_="row").find_all('div')[0].contents[0]
            title = reviewItem.find(class_='_2xg6Ul').contents[0]
            description = reviewItem.find(class_='qwjRop').find(class_="").find(class_="").contents[0]
            data.append({
            'source': 'Flipkart',    
            'product': productName.lower(),     
            'title': title,
            'rating': rating,
            'description': description
            })
            #print(data)
    x = reviewsCol.insert_many(data)
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

@app.route('/api/v1.0/weather', methods=['POST'])
def weather():
    #req = json.loads(request.body)
    #get action from json 
    #action = req.get('queryResult').get('action') 
    message = ''
    bodyParams = request.get_json()
    action = bodyParams['queryResult']['action']
    city = bodyParams['queryResult']['parameters']['geo-city']
    #print('ssssssssssss  ', bodyParams)
    if action == 'get_weather':
        weatherurl = 'https://api.openweathermap.org/data/2.5/weather?q='+city+'&appid=a716f2f5ebcee25f134cb1032217904f'
        weatherInfo = requests.get(weatherurl)   
        message = weatherInfo.json()['weather'][0]['description']

    #print("==========", weatherData['weather'][0]['description']) 
    r = {
            "speech" : "hello",
            "fulfillmentText": "Weather of "+city+" is "+message,
            "source" : "wwatherAPI=="+weatherInfo.json()['weather'][0]['description']
        }    
    
    return jsonify(r)

def sendEmail(student):
    # Send the Email to Student
    import smtplib, ssl
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.message import EmailMessage

    context = ssl.create_default_context()
    msg = EmailMessage()
    #msg = MIMEMultipart('alternative')
    msg['Subject'] = "Registration Completed."
    msg['From'] = 'skg17nov@gmail.com'
    msg['To'] = student['emailId']

    # Create the body of the message (a plain-text and an HTML version).
    #text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html1 = """<html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Demystifying Email Design</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    </head>
    <body bgcolor="#33bbff">
        <div style="background-color:#33bbff;height:400px;color:#00008b;padding:30px;font-size:14px;">
            <div><img width="200px" height="80px" src="https://ineuron.ai/wp-content/uploads/2019/09/Ineuron-Logo-white.png"></div>
            <div>
                <p>Dear {name},<br>
                Your registration has been completed.<br>
                Please visit our website <a href="https://ineuron.ai/">ineuron.ai</a> for more information.
                </p>
            </div>
            <div>
                Thank You!
            </div>
        </div>
    </body>
    </html>""".format(name=student["name"])
    msg.set_content(html1, subtype='html')
    # Record the MIME types of both parts - text/plain and text/html.
    #part1 = MIMEText(text, 'plain')
    #part2 = MIMEText(html, 'html')
    #msg.set_payload(html)
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    #msg.attach(part1)
    #msg.attach(part2)
    #msg.add_header('Content-Type','text/html')
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls(context=context) 
    s.login("skg17nov@gmail.com", "Sapple123") 
    s.sendmail(msg['From'], msg['To'] , msg.as_string()) 
    s.quit()
    
def sendSMS(student):
    message= "Thanks "+student['name']+" for your enquiry. We will get back to you soon."
    phoneNumber = student['mobileNo']
    url = "https://www.fast2sms.com/dev/bulk"
    payload = "sender_id=FSTSMS&message="+message+"&language=english&route=p&numbers="+phoneNumber
    headers = {
                'authorization': "WKSZYFTUpljeX3JCVMiBbdA96fnquLI7sNk5yPa0EgGt2c1rRzJ9n1cVZWR2rHQi0mLdjuBa5sYfktob",
                'Content-Type': "application/x-www-form-urlencoded",
                'Cache-Control': "no-cache"}
    response = requests.request("POST", url, data=payload, headers=headers)
    return {'message': response.text}
    
    
@app.route('/api/v1.0/signUp', methods=['POST'])
def signUp():
    message = ''
    bodyParams = request.get_json()
    action = bodyParams['queryResult']['action']
    if action == 'student_signup':
        student = {
        'name':  bodyParams['queryResult']['parameters']['name'],
        'emailId': bodyParams['queryResult']['parameters']['email'],
        'mobileNo': bodyParams['queryResult']['parameters']['mobileNo'],
        'qualification': bodyParams['queryResult']['parameters']['qualification'],
        'courseName': bodyParams['queryResult']['parameters']['courseName']
        }
        mycol = mydb["students"]
        x = mycol.insert_one(student)
        insereted_id = x.inserted_id
        message = 'Thank You. We will send all the course details in your Email.'
        sendEmail(student)
        sendSMS(student)
        r = {
            "speech" : "Student SignUp",
            "fulfillmentText": message,
            "source" : "Academic"
        }    
    
    return jsonify(r)




if __name__ == "__main__":
    app.run(debug = True)




    
