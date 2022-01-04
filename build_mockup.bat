PYTHONPATH=mockup
python build.py mockup/schema.json mockup/generated
sphinx-build mockup/generated/doc mockup/generated/doc/build -b singlehtml
python -m unittest discover -s mockup/generated