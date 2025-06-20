# Sakila Image Generator

A Python script that uses AI to generate posters for films in the MySQL _sakila_ demo database.

## Tools needed

* [Python 3.x](https://www.python.org/downloads/) with all its binary utilities, **pip** in particular. 
* A code editor like [VS Code](https://code.visualstudio.com/download), [PyCharm](https://www.jetbrains.com/pycharm/download), [IntelliJ Idea](https://www.jetbrains.com/idea/download) or any other.
* A running instance of **MySQL** server with the __sakila__ demo database installed on it.

## How to run the script?

### On Linux and macOS

1. Create a **.env** file by duplicating, renaming and editing the supplied **.env.prototype** file.
2. Create a virtual environment:

````shell
python3 -m venv venv
````
3. Activate the virtual environment:

````shell
source venv/bin/activate
````

4. Install the dependencies

````shell
pip3 install -r requirements.txt
````

5. Launch the script

````shell
python3 main.py
````

### On Windows

1. Create a **.env** file as described in the _Linux_ section.
2. Create a virtual environment:

````shell
python -m venv venv
````
3. Activate the virtual environment:

````shell
venv\Scripts\activate
````

4. Install the dependencies

````shell
pip install -r requirements.txt
````

5. Launch the script

````shell
python main.py
````
