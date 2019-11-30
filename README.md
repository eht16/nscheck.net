# nscheck.net


## About

`nscheck.net` is a set of DNS utilities to lookup a
PTR records (reverse DNS) including the authoritative nameservers
as well as querying glue records for domains.

While there are tons of such tools already available,
glue record lookup and authoritative nameservers for PTR
records are rather seldom. Hence this project.


## Configuration

Copy `config.py` to `config_local.py` and edit it as needed.
Both configuration files are used and settings in `config_local.py`
will override those in `config.py`.


## Running

`nscheck.net` requires Python 3.x.
First you should install the requirements, ideally in a virtualenv:

	python3 -m venv venv
	venv/bin/pip install -r requirements.txt


### Run locally / Development

	FLASK_APP=nscheck FLASK_ENV=development venv/bin/flask run


### Run in production

	venv/bin/uwsgi --master --processes 4 --manage-script-name --mount /=nscheck:wsgi


## License

nscheck.net is licensed under the MIT License.


## Author

Enrico Tröger <enrico.troeger@uvena.de>
