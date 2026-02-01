.PHONY: lint test local-up migrate smoke

lint:
	./scripts/lint.sh

test:
	./scripts/test.sh

local-up:
	./scripts/local_up.sh

migrate:
	./scripts/db_migrate.sh

smoke:
	./scripts/smoke_test.sh
