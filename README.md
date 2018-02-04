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
| utils       | utilities                               |
| frontend    | frontend files (js, css)                |

Put unit tests under `tests/` folder.

## Install the requirements

### Python
```
pip install -r requirements.txt
```

### Javascript
```
npm install
```

## Run the server

First run the webpack watcher:
```
npm run watch
```

Then the flask server:

```
python manage.py runserver
```


## Run Unittest
```
python manage.py test
```


## Demo pages

* `http://localhost:5000/api/demo/hello`

The server will echo back the message using json, you can change `hello` to any other string.

* `http://localhost:5000/pages/demo/`

Demo page, build by MDUI.