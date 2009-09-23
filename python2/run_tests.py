# -*- coding: utf-8 -*-

import sys
import unittest
import berrymq.berrymq as berrymq


def show_usage(alert_version=False):
    print("""berryMQ tests
  for Python 2.4, 2.5, 2.6 (current interpreter: %d.%d.%d)

  run_tests.py [option] target:

  *target
    --all:      run all test
    --basic:    test basic features only
    --pull:     test pull API
    --parallel: test multithreading feature only(slow)
    --jsonrpc:  test jsonrpc components(slow)
    --1st_node: network test(run this first)
    --2nd_node: network test(run this later)
""" % sys.version_info[:3])
    if alert_version:
        print("This test is able to be run on Python 2.X")
    sys.exit()


def main():
    if sys.version_info[0] != 2:
        show_usage(alert_version=True)

    if len(sys.argv) == 1 or "--help" in sys.argv or "-h" in sys.argv:
        show_usage()

    if "--1st_node" in sys.argv:
        import tests.test_interprocess
        tests.test_interprocess.primary_node()
        sys.exit()
    if "--2nd_node" in sys.argv:
        import tests.test_interprocess
        tests.test_interprocess.secondary_node()
        sys.exit()

    suite = unittest.TestSuite()

    if "--basic" in sys.argv or "--all" in sys.argv:
        import tests.test_berrymq
        suite.addTest(tests.test_berrymq.test_setup(berrymq))

    if "--pull" in sys.argv or "--all" in sys.argv:
        import tests.test_berrymq_pull
        suite.addTest(tests.test_berrymq_pull.test_setup(berrymq))

    if "--parallel" in sys.argv or "--all" in sys.argv:
        import tests.test_berrymq_parallel
        suite.addTest(tests.test_berrymq_parallel.test_setup(berrymq))

    if "--jsonrpc" in sys.argv or "--all" in sys.argv:
        import tests.test_jsonrpc
        suite.addTest(tests.test_jsonrpc.test_setup())

    if suite.countTestCases():
        runner = unittest.TextTestRunner()
        runner.run(suite)
    else:
        show_usage()


if __name__ == "__main__":
    main()
