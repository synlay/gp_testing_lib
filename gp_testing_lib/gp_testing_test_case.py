# -*- coding: utf-8 -*-
import re

class GertrudTestCase:
    def __init__(self, object_count=None, value_rules=dict()):
        self.object_count = object_count
        self.value_rules = value_rules

    def assert_description(index, custom_message):
        return "Test Rule [" + str(index + 1) + "]: " + custom_message


class GertrudTestCaseRule:
    def __init__(self, rule=None):
        self.rule = rule

    def compare(self, value):
        raise NotImplementedError( "Should have implemented this" )

    def __str__(self):
        return str(self.rule)


class GertrudTestCaseRuleRe(GertrudTestCaseRule):
    def compare(self, value):
        return re.match(self.rule, value) is not None


class GertrudTestCaseRuleEq(GertrudTestCaseRule):
    def compare(self, value):
        return self.rule == value

    def __eq__(self, value):
        return self.rule == value.rule if isinstance(value, GertrudTestCaseRuleEq) else False


GERTRUD_TEST_CASE_EQ_NONE = GertrudTestCaseRuleEq(None)


class GertrudTestCaseRuleIterator(GertrudTestCaseRule):
    def __init__(self, object_count, rules=None):
        super().__init__(rules)
        self.test_cases = GertrudTestCase(object_count, rules)

    def compare(self, attributes):
        assert len(attributes) == self.test_cases.object_count

        normalizes_attributes = {attribute["key"]: attribute["value"].pop() if attribute["value"] else None for attribute in attributes}

        for key, value_rules in self.test_cases.value_rules.items():
            assert key in normalizes_attributes

            column_values = normalizes_attributes[key]

            if not value_rules == GERTRUD_TEST_CASE_EQ_NONE:
                # assert len(value_rules) == len(column_values)

                value_rules_dict = dict(value_rules)

                for column_name, column_rule in value_rules:
                    assert column_name in column_values

                    # Check if the regular expression from the defined value matching rule does match the actual column
                    assert column_rule.compare(column_values[column_name]), "Column value: '" + \
                           str(column_values[column_name]) + "' didn't match '" + \
                           str(column_rule) + "' for attribute key: '" + str(column_name) + "'"

                    # del column_values[column_name]
                    del value_rules_dict[column_name]

                # Check if all defined ruled were analyzed
                assert len(value_rules_dict) == 0, "Some defined attributes rules '" + \
                       str(value_rules_dict) + "' were not processed"
            else:
                assert column_values is None

            del normalizes_attributes[key]

        # Check if all defined ruled were analyzed
        return len(normalizes_attributes) == 0
