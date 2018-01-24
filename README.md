# DPass
This is the web based app of DPass.

Files under `app/` folder:

| folder/file | description                             |
| ----------- | --------------------------------------- |
| api         | code for api                            |
| models      | database models                         |
| static      | static html/js/css files                |
| templates   | dynamic html files (server side render) |
| views       | code for serving dynamic pages          |


## Install the requirements

```
pip install -r requirements.txt
```

## Run the server

Run
```
python manager.py runserver
```
in the terminal


## Demo pages

* `http://localhost:5000/api/demo/hello`

The server will echo back the message using json, you can change `hello` to any other string.

* `http://localhost:5000/pages/demo/`

Demo page for school shuttle bus (build with jQuery, bootstrap and some other icon libraries).