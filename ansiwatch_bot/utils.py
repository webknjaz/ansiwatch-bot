from contextlib import contextmanager
from functools import partial
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import cherrypy


bus_log = partial(cherrypy.engine.publish, 'log')


@contextmanager
def separate_git_worktree(orig_repo, git_branch):
    with TemporaryDirectory(prefix=f'ansiwatch_bot--pr--') as tmp_dir:
        tmp_repo_path = Path(tmp_dir) / 'repo'
        git_diff_proc = subprocess.run(
            # FIXME: replace with 'git worktree' once Git v2.5+ is there
            ('/usr/share/git/contrib/workdir/git-new-workdir',
             orig_repo, tmp_repo_path, git_branch),
        )
        yield tmp_repo_path
