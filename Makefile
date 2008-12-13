all:
	echo "Nothing to make here."

clean:
	find -name "*.pyc" -or -name "*.pyo" -or -name "*~" -exec rm -f {} \;
	rm -f httpd_data/templates/*
