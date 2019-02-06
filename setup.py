#! /usr/bin/env python

import subprocess

subprocess.check_output(('su', '-c', 'yum upgrade git'))
