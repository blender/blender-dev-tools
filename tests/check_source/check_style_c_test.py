#!/usr/bin/env python3

# ----
import os
import sys
sys.path.append(
        os.path.join(
        os.path.dirname(__file__),
        "..", "..", "check_source",
        ))
# ----

import unittest

warnings = []
import check_style_c
check_style_c.print = warnings.append

# ----
parser = check_style_c.create_parser()
# dummy, not used at the moment
args = parser.parse_args(["."])
# ----

FUNC_BEGIN = """
void func(void)
{
"""
FUNC_END = """
}"""


def test_code(code):
    warnings.clear()
    check_style_c.scan_source("test.c", code, args)
    err_ls = [w.split(":", 3)[2].strip() for w in warnings]
    # print(warnings)
    return err_ls


class SourceCodeTest(unittest.TestCase):
    def test_brace_function(self):
        # --------------------------------------------------------------------
        # brace on not on newline (function)
        code = """
void func(void) {
\t/* pass */
}"""
        err_ls = test_code(code)
        self.assertEqual(1, len(err_ls))
        self.assertEqual("E101", err_ls[0])

        code = """
void func(void)
{
\t/* pass */
}"""
        err_ls = test_code(code)
        self.assertEqual(0, len(err_ls))

    def test_brace_kw(self):
        # --------------------------------------------------------------------
        # brace on on newline (if, for... )

        code = FUNC_BEGIN + """
\tif (1)
\t{
\t\t/* pass */
\t}""" + FUNC_END
        err_ls = test_code(code)
        self.assertEqual(1, len(err_ls))
        self.assertEqual("E108", err_ls[0])

        code = FUNC_BEGIN + """
\tif (1) {
\t\t/* pass */
\t}""" + FUNC_END
        err_ls = test_code(code)
        self.assertEqual(0, len(err_ls))

    def test_brace_do_while(self):
        # --------------------------------------------------------------------
        # brace on on newline do, while

        code = FUNC_BEGIN + """
\tif (1)
\t{
\t\t/* pass */
\t}""" + FUNC_END
        err_ls = test_code(code)
        self.assertEqual(1, len(err_ls))
        self.assertEqual("E108", err_ls[0])

        code = FUNC_BEGIN + """
\tif (1) {
\t\t/* pass */
\t}""" + FUNC_END
        err_ls = test_code(code)
        self.assertEqual(0, len(err_ls))

    def test_brace_kw_multiline(self):
        # --------------------------------------------------------------------
        # brace-multi-line

        code = FUNC_BEGIN + """
\tif (a &&
\t    b) {
\t\t/* pass */
\t}""" + FUNC_END
        err_ls = test_code(code)
        self.assertEqual(2, len(err_ls))
        self.assertEqual("E103", err_ls[0])
        self.assertEqual("E104", err_ls[1])

        code = FUNC_BEGIN + """
\tif (a &&
\t    b)
\t{
\t\t/* pass */
\t}""" + FUNC_END

        err_ls = test_code(code)
        self.assertEqual(0, len(err_ls))

    def test_brace_indent(self):
        # --------------------------------------------------------------------
        # do {} while (1);
        code = FUNC_BEGIN + """
\tif (1) {
\t\t/* pass */
\t\t}""" + FUNC_END
        err_ls = test_code(code)
        self.assertEqual(1, len(err_ls))
        self.assertEqual("E104", err_ls[0])

        code = FUNC_BEGIN + """
\tif (1) {
\t\t/* pass */
\t}""" + FUNC_END
        err_ls = test_code(code)
        self.assertEqual(0, len(err_ls))


if __name__ == '__main__':
    unittest.main(exit=False)
