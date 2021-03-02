# Inventory Manager

## Prerequisites

Before you begin, ensure you have met the following requirements:
* You have an Internet browser (Chrome, Firefox, Safari, etc)
* You have a code editor (VS Code, Atom, etc)
* You have python3 and pip

## Installation

To install, follow these steps:

Via Downloading from GitHub:
1. Download this repository onto your machine by clicking the "Clone or Download" button or Fork the repo into your own Github account
2. Download and extract the zip file to a directory of your choice.

Via command line:
```
$ git clone https://github.com/puglisac/inventory_manager.git
```


Backend Environment Setup:
1. In the directory you've cloned or downloaded the repo to, create the virtual environment and activate it

```
$ python3 -m venv venv
$ source venv/bin/activate
```

2. Install dependencies

```
(venv)$ pip3 install -r requirements.txt
```
3. [Install PostgreSQL](https://www.postgresql.org/download/) if you do not have it.

4. Create a database
```
$ createdb inventory_manager
```
5. Head over to [N2YO](https://www.n2yo.com/login/) and register for an account

7. Start up the Flask server
```
(venv)$ flask run
```
8. Navigate your preferred browser (Chrome suggested) to http://127.0.0.1:5000/
