#! /bin/sh

echo "RUNNING PYLINT ======================"
pylint --recursive y *.py

echo
echo "RUNNING PYDOCSTYLE =================="
pydocstyle *.py
pydocstyle src/*.py
pydocstyle test/*.py

echo
echo "RUNNING MYPY ========================"
mypy .

echo
echo "RUNNING UNIT TESTS =================="
python ./unit_tests.py

# TO_DO: add check to validate all test files
#        have been added to unit_tests.py
