# weshareCOSutils
This projects provides api for the front end to call and get service from aws s3
# Install the dependencies
## To use the environment variables
pip install django-environ 
## Cross-domain
pip install django-cors-headers
## User the AWS Common Runtime (CRT)
pip install boto[crt]
## Configuration
aws configure
input your aws access key id
input your aws secret access key
input your default region(ap-east-1)
# Start the app (you can assign the port arbitrarily)
python manage.py runserver 8181
