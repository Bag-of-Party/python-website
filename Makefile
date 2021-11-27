test: 
	python -m pytest -v tests 

rundocker:
	docker run -p 2345:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres