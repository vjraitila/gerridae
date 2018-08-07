extract_translations:
	pybabel extract -F babel.cfg -o messages.pot gerridae
	pybabel update -i messages.pot -d gerridae/translations

compile_translations:
	pybabel compile -d gerridae/translations