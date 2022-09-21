######################################################
#
# PyRAI2MD test grid search
#
# Author Jingbai Li
# Oct 11 2021
#
######################################################

import os
import shutil
import subprocess

try:
    import PyRAI2MD

    pyrai2mddir = os.path.dirname(PyRAI2MD.__file__)

except ModuleNotFoundError:
    pyrai2mddir = ''


def TestGridSearch():
    """ grid search test

    1. energy grad soc grid search
    2. retrieve data

    """

    testdir = '%s/results/grid_search' % (os.getcwd())
    record = {
        'egs': 'FileNotFound',
        'egs_search': 'FileNotFound',
        'egs_retrieve': 'FileNotFound',
    }

    filepath = './grid_search/search_data/egs.json'
    if os.path.exists(filepath):
        record['egs'] = filepath

    filepath = './grid_search/search_data/egs_search'
    if os.path.exists(filepath):
        record['egs_search'] = filepath

    filepath = './grid_search/search_data/egs_retrieve'
    if os.path.exists(filepath):
        record['egs_retrieve'] = filepath

    summary = """
 *---------------------------------------------------*
 |                                                   |
 |             Grid Search Test Calculation          |
 |                                                   |
 *---------------------------------------------------*

 Check files and settings:
-------------------------------------------------------
"""
    for key, location in record.items():
        summary += ' %-10s %s\n' % (key, location)

    for key, location in record.items():
        if location == 'FileNotFound':
            summary += '\n Test files are incomplete, please download it again, skip test\n\n'
            return summary, 'FAILED(test file unavailable)'
        if location == 'VariableNotFound':
            summary += '\n Environment variables are not set, cannot find program, skip test\n\n'
            return summary, 'FAILED(environment variable missing)'

    CopyInput(record, testdir)

    summary += """
 Copy files:
 %-10s --> %s/egs.json
 %-10s --> %s/egs_search
 %-10s --> %s/egs_retrieve

 Run MOLCAS CASSCF:
""" % ('egs', testdir,
       'egs_search', testdir,
       'egs_retrieve', testdir)

    results, code = RunNN(testdir)

    summary += """
-------------------------------------------------------
                Grid Search OUTPUT
-------------------------------------------------------
%s
-------------------------------------------------------
""" % results
    return summary, code


def CopyInput(record, testdir):
    if not os.path.exists(testdir):
        os.makedirs(testdir)

    shutil.copy2(record['egs'], '%s/egs.json' % testdir)
    shutil.copy2(record['egs_search'], '%s/egs_search' % testdir)
    shutil.copy2(record['egs_retrieve'], '%s/egs_retrieve' % testdir)


def Collect(testdir, title):
    with open('%s/%s.log' % (testdir, title), 'r') as logfile:
        log = logfile.read().splitlines()

    results = []
    for n, line in enumerate(log):
        if """ Number of search:""" in line:
            results = log[n - 1:]
            break
    results = '\n'.join(results) + '\n'

    return results


def RunNN(testdir):
    maindir = os.getcwd()
    results = ''

    os.chdir(testdir)
    subprocess.run('pyrai2md egs_search > stdout', shell=True)
    os.chdir(maindir)
    tmp = Collect(testdir, 'egs')
    results += tmp

    subprocess.run('mv %s/egs.log %s/egs.log.search' % (testdir, testdir), shell=True)

    if len(tmp.splitlines()) < 4:
        code = 'FAILED(egs grid search runtime error)'
        return results, code
    else:
        results += ' grid search done, entering data retrieving test\n'

    os.chdir(testdir)
    subprocess.run('pyrai2md egs_retrieve >> stdout', shell=True)
    os.chdir(maindir)
    tmp = Collect(testdir, 'egs')
    results += tmp

    if len(tmp.splitlines()) < 4:
        code = 'FAILED(egs data retrieving runtime error)'
        return results, code
    else:
        code = 'PASSED'
        results += ' data retrieving done\n'

    return results, code
