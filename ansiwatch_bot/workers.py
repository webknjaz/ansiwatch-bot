import pathlib
import subprocess

import cherrypy


GITHUB_REPO_URL_TMPL = 'git://github.com/{slug}.git'


def get_git_separate_dir_args(path):
    path_str = str(path)
    return f'--git-dir={path_str}/.git', f'--work-tree={path_str}/'
    return '-C', path_str  # This'd work in Git v1.8.5+
    # Post note: since Git v2.3.4+ it processes empty path arg correctly


def sync_repo(repo, path):
    git_args = get_git_separate_dir_args(path)
    git_exec_cmd = 'git', *git_args

    cherrypy.engine.log(f'Starting to sync repo {repo}...')
    if not (path / '.git').exists():
        cherrypy.engine.log(f'Cloning repo {repo}...')
        subprocess.check_output(
            ('git', 'clone', GITHUB_REPO_URL_TMPL.format(slug=repo), path)
        )
        cherrypy.engine.log(f'Adding refs/pull/*/head to repo {repo} config...')
        subprocess.check_output(
            (*git_exec_cmd, 'config', '--add', 'remote.origin.fetch',
             '+refs/pull/*/head:refs/pull/origin/*')
        )
        cherrypy.engine.log(f'Adding refs/pull/*/merge to repo {repo} config...')
        subprocess.check_output(
            (*git_exec_cmd, 'config', '--add', 'remote.origin.fetch',
             '+refs/pull/*/merge:refs/pull-merge/origin/*')
        )

    cherrypy.engine.log(f'Fetching repo {repo}...')
    subprocess.check_output(
        (*git_exec_cmd, 'fetch', '--all')
    )


def test_repo(repo_slug, local_repo, pr):
    git_args = get_git_separate_dir_args(local_repo)
    git_exec_cmd = 'git', *git_args
    cherrypy.engine.log(f'Starting to test {pr} in repo {repo_slug}...')
    git_diff_proc = subprocess.Popen(
        (*git_exec_cmd, 'diff', f'...refs/pull-merge/origin/{pr}'),
        stdout=subprocess.PIPE,
    )
    git_diff_proc = subprocess.run(
        (pathlib.Path.cwd() / 'py2venv/bin/ansible-review', ),
        stdin=git_diff_proc.stdout,
        check=True,
        cwd=local_repo,
    )
