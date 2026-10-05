#!/usr/bin/env python3
"""يشغّل ملفات الاختبار ذات أسماء kebab-case ويرفض نجاح مجموعة فارغة."""
import importlib.util
from pathlib import Path
import unittest


def main():
    suite = unittest.TestSuite()
    for index, path in enumerate(sorted((Path(__file__).resolve().parents[1] / 'tests').glob('test-*.py'))):
        spec = importlib.util.spec_from_file_location('plugin_test_%d' % index, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
    if suite.countTestCases() == 0:
        print('ERROR: no tests discovered')
        return 1
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
