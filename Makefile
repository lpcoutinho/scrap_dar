.PHONY: format tmux_create tmux run

format:
	@isort .
	@black .

create_venv:
	python3 -m venv venv && pip install -r requirements.txt

tmux_create:
	tmux new -s fastapi

tmux:
	tmux attach -t fastapi
run:
	xvfb-run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
