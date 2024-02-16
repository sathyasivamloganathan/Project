from pymongo import MongoClient

client = MongoClient("mongodb+srv://sathyasivam2004:Ng0cdhFjSIhlzAkt@cluster0.jkuqovx.mongodb.net/")
db = client['mri']
collection = db['abha']

data = [
    {
        "userName": "Ramkumar K",
        "userEmail": "ramkumar.k.2021.ece@ritchennai.edu.in",
        "userMobile": "9360540209",
        "abhaNumber": "43927693740933",
        "dateOfBirth": "2002-11-30",
        "place": "Arcot",
        "gender": "male",
        "patientId": "1001",    
    },
    {
        "userName": "Prathish Kumar T",
        "userEmail": "prathishkumar.t.2021.ece@ritchennai.edu.in",
        "userMobile": "9894663980",
        "abhaNumber": "88479208638590",
        "dateOfBirth": "2004-08-23",
        "place": "Vellore",
        "gender": "male",
        "patientId": "1002",    
    },
    {
        "userName": "Jayakumar B",
        "userEmail": "jayakumar.b.2021.cse@ritchennai.edu.in",
        "userMobile": "8667681698",
        "abhaNumber": "35659037557937",
        "dateOfBirth": "2004-06-02",
        "place": "Thirupur",
        "gender": "male",
        "patientId": "1003",    
    },
    {
        "userName": "Sathya Sivam L",
        "userEmail": "sathyasivam2004@gmail.com",
        "userMobile": "8925461916",
        "abhaNumber": "88302810856382",
        "dateOfBirth": "2004-03-01",
        "place": "Chennai",
        "gender": "male",
        "patientId": "1004",    
    },
]

collection.insert_many(data)