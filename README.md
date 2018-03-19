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
pip install -r requirements.dev.txt
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
python run.py --develop
```

If you want to use ethereum:
```
python run.py --develop --use_ethereum
```
Please ensure that you have initialized the ethereum block chain before.


## Run Unittest
```
python manage.py test
```


