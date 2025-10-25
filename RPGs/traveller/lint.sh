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

# TO_DO: add check to validate all test files
#        have been added to unit_tests.py
