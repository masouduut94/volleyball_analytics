install: requirements.txt
	@pip install -r requirements.txt
clean:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	rm -rf `find -type d -name .ipynb_checkpoints`
check:
	ruff check .
test:
	@python -m unittest discover src/backend/app/tests
	@echo "Finished !!!"