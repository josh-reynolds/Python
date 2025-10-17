#! /bin/sh

echo "RUNNING PYLINT ======================"
pylint *.py

echo
echo "RUNNING PYDOCSTYLE =================="
pydocstyle *.py

echo
echo "RUNNING MYPY ========================"
mypy *.py

echo
echo "RUNNING UNIT TESTS =================="
python ./unit_tests.py

