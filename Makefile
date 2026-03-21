.PHONY: lint type test format install-hooks

lint:
	uv run ruff check .

type:
	uv run mypy --package corvus-corone --package corvus-corone-pilot

test:
	uv run pytest

format:
	uv run ruff format .

install-hooks:
	cp scripts/pre-push .git/hooks/pre-push
	sed -i 's/\r//' .git/hooks/pre-push
	chmod +x .git/hooks/pre-push
	@echo "pre-push hook installed."
