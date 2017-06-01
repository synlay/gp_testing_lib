# -*- coding: utf-8 -*-
import json
import glob
import re
import os

from gp_testing_test_case import GertrudTestCase

class GertrudTesting:

    def execute_import_error_rules(import_errors, test_rules):
        # Check if the count of defined rules matches with the count of existing import errors
        assert len(import_errors) == len(test_rules), "The count of found import errors files differ from the count of defined test rules"

        for filename, file_path in import_errors.items():

            assert filename in test_rules, "Test if there is an error case defined for the found error file"

            gp_test_case = test_rules[filename]
            found_error_count = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                # Iterate over every data line from the current export file
                for line in f:
                    found_error_count += 1
                    error_dict = json.loads(line)

                    details_matched = False

                    assert error_dict.get("error_code") in gp_test_case.value_rules, \
                           "No rules found for error code: '" + str(error_dict.get("error_code")) + "'"
                    # Iterate over all defined error rules for the the error code
                    for column_rules in gp_test_case.value_rules[error_dict.get("error_code")]:
                        details_matched = len(column_rules) > 0
                        # Iterate over all colum rules
                        for column_name, column_re in column_rules:
                            # Check if the regular expression from the defined value matching rule does match the actual column
                            details_matched = details_matched and re.match(column_re, error_dict.get(column_name))
                        if details_matched:
                            break

                    assert details_matched, "One or more columns didn't match for error code: '" + str(error_dict.get("error_code")) + "'"

            assert found_error_count == gp_test_case.object_count, "The count of import errors in one file differs from the one defined in test rules"


    def execute_test_rules(exports, test_rules):
        export_list = list(exports)
        # Check if the count of defined rules matches with the count of existing exports
        assert len(export_list) == len(test_rules), "The count of found export files differ from the count of defined test rules"

        for index, (full_filename, delta_filename) in enumerate(export_list):

            full_test_case = test_rules[index][0]
            delta_test_case = test_rules[index][1]

            assert (full_test_case is None and full_filename is None) or \
                   (full_test_case is not None and full_filename is not None), \
                   GertrudTestCase.assert_description(index, "there should" + ("n't" if full_test_case is None else "") + " be a full export")
            assert (delta_test_case is None and delta_filename is None) or \
                   (delta_test_case is not None and delta_filename is not None), \
                   GertrudTestCase.assert_description(index, "there should" + ("n't" if delta_test_case is None else "") + " be a delta export")

            iterate_testcases = filter(lambda test: test[0] is not None, [(full_filename, full_test_case),
                                                                          (delta_filename, delta_test_case)])

            # Iterate over full test cases and maybe delta test cases
            for filename, test_case in iterate_testcases:
                with open(filename, 'r', encoding='utf-8') as f:
                    # Ignore Header Line
                    f.readline()
                    object_count = 0
                    missed_rules = test_case.value_rules

                    # Iterate over every data line from the current export file
                    for line in f:
                        object_count += 1
                        gp_export_obj = GertrudExport(line)

                        # Check if a test rule for the current PID line can be found
                        assert gp_export_obj.get_key('pid') in missed_rules, \
                               GertrudTestCase.assert_description(index, " PID: '" + gp_export_obj.get_key('pid') + \
                               "' doesn't exist in defined test rules")

                        # Iterate over all defined vaule matching rules for the specific PID
                        for column_name, column_rule in missed_rules[gp_export_obj.get_key('pid')]:
                            # Check if the regular expression from the defined value matching rule does match the actual column
                            assert column_rule.compare(gp_export_obj.get_key(column_name)), \
                                   GertrudTestCase.assert_description(index, " column value: '" + \
                                   str(gp_export_obj.get_key(column_name)) + "' didn't match '" + \
                                   str(column_rule) + "' for pid: '" + gp_export_obj.get_key('pid') + "'")

                        # Remove the passed PID value rule
                        del missed_rules[gp_export_obj.get_key('pid')]

                    # Check if the defined count of objects matches
                    assert test_case.object_count == object_count
                    # Check if all defined ruled were analyzed
                    assert len(missed_rules) == 0, GertrudTestCase.assert_description(index, " some defined test rules '" + \
                           missed_rules +"' were missing in the export")


class GertrudImport:
    def get_error_files():
        return {os.path.basename(file).split(".gpi_error_log")[0]: file for file in glob.glob("../data/*.gpi_error_log")}


class GertrudExport:
    def __init__(self, json_row=None):
        self.__items = dict()
        if json_row:
            for key, value in json.loads(json_row).items():
                self.__items[key] = value['value'] if type(value) is dict else value

    def get_key(self, name):
        return self.__items[name]

    def __str__(self):
        return "PID: " + self.__items['pid'] + ", Bezeichnung: " +  self.__items['Bezeichnung'] + ", State: " +  self.__items['_state']

    def get_full_and_delta_export_tuples(all_export_wildcard_pattern, delta_export_wildcard_pattern):
        all_exports = glob.glob(all_export_wildcard_pattern)
        delta_exports = glob.glob(delta_export_wildcard_pattern)
        full_exports = list(set(all_exports) - set(delta_exports))
        delta_diff = len(full_exports) - len(delta_exports)

        full_exports.sort()
        delta_exports.sort()

        return zip(full_exports, [None for x in range(delta_diff)] + delta_exports if delta_diff > 0 else delta_exports)
