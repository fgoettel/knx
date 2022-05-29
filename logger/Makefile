.PHONY: codegen doc

codegen:  ## Generate new mapping and orm
	poetry run python -m logger.codegen.gen_dtype_matcher
	poetry run python -m logger.codegen.gen_orm

doc: ## Collection of interesting data
    # TODO: Add coverage
	poetry run pyreverse -o png -p logger ./logger
