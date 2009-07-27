# -*- coding: utf-8 -*-

import sys

def show_usage(alert_version=False):
    print("""berryMQ tests
  for Python 2.5, 2.6 (current interpreter: %d.%d.%d)

  run_tests.py [option] target:

  *option
    --single-thread

  *target
    --all:      run all test
    --basic:    test basic features only
    --parallel: test multithreading feature only(slow)
    --1st_node: network test(run this first)
    --2nd_node: network test(run this later)
""" % sys.version_info[:3])
    if alert_version:
        print("This test is able to be run on Python 2.X")
    sys.exit()

def main():
    is_run = False

    if sys.version_info[0] != 2:
        show_usage(alert_version=True)

    if len(sys.argv) == 1 or "--help" in sys.argv or "-h" in sys.argv:
        show_usage()

    if "--1st_node" in sys.argv:
        import berrymq
        import tests.test_berrymq_network_1st_node
        tests.test_berrymq_network_1st_node.test(mqas)
        sys.exit()
    if "--2nd_node" in sys.argv:
        import berrymq
        import tests.test_berrymq_network_2nd_node
        tests.test_berrymq_network_2nd_node.test(berrymq)
        sys.exit()

    if "--single-thread" in sys.argv:
        import berrymq_singlethread.berrymq as berrymq
    else:
        import berrymq.berrymq as berrymq

    if "--basic" in sys.argv or "--all" in sys.argv:
        import tests.test_berrymq
        tests.test_berrymq.test(berrymq)
        is_run = True

    if "--parallel" in sys.argv or "--all" in sys.argv:
        import tests.test_berrymq_parallel
        tests.test_berrymq_parallel.test(berrymq)
        is_run = True

    if not is_run:
        show_usage()


if __name__ == "__main__":
    main()


