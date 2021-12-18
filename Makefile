test: 
	python -m pytest -vv tests 

test-api: 
	python -m pytest -vv tests/test_api.py

test-one: 
	python -m pytest -vv tests -k test_delete_item_no_contents

rundocker:
	docker run -p 2345:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres


test-cov:
	python -m pytest tests --cov app

show-cov:
	coverage html