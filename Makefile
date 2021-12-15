test: 
	python -m pytest -vv tests 

rundocker:
	docker run -p 2345:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres


test-cov:
	python -m pytest tests --cov app

show-cov:
	coverage html