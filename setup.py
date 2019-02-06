#! /usr/bin/env python

import subprocess

subprocess.check_output(('yum', 'upgrade', 'git'))
