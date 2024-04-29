# Gmail_reading
Python code to read emails from gmail using google Gmail API

# Requirements to install this project
Python - 3.9.2
Django - 4.2.11
PostgreSQL - v10 or above

# Link to create and enable the Gmail API using google account
https://console.cloud.google.com/apis/credentials?project=crested-grove-421405

# Install pip
sudo apt install -y python3-pip

# Install the virtual env
sudo apt install -y python3-venv

# Create a virtual env in ubuntu 20.04
python3 -m venv my_env [replace my_env with your enn name you want to use]

# Activate the virtual env
source my_env/bin/activate

# Install the project requirements inside the virtual env
pip install -r requirements.txt

# Run the project
python manage.py runserver
