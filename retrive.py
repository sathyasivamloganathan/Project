from pymongo import MongoClient
from gridfs import GridFS

# Connect to MongoDB
try:
    with MongoClient('mongodb+srv://sathyasivam2004:Ng0cdhFjSIhlzAkt@cluster0.jkuqovx.mongodb.net') as client:
        db = client['mri']
        grid_fs = GridFS(db, collection='report')

        # Retrieve a file from GridFS by its filename
        file_cursor = grid_fs.find_one({'filename': 'gomk.pdf'})

        if file_cursor is not None:
            # Get the file content
            file_content = file_cursor.read()

            # Do something with the file content (e.g., save it to a new file)
            with open('C:\\Users\\Sathya Sivam\\Downloads\\LT\\Output\\gomk.pdf', 'wb') as downloaded_file:
                downloaded_file.write(file_content)
        else:
            print("File not found in GridFS.")
except Exception as e:
    print("An error occurred:", e)
