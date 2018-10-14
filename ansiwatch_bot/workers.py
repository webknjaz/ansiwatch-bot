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

    cherrypy.engine.log(f'Starting to sync repo {repo}...')
    if not (path / '.git').exists():
        cherrypy.engine.log(f'Cloning repo {repo}...')
        subprocess.check_output(
            ('git', 'clone', GITHUB_REPO_URL_TMPL.format(slug=repo), path)
        )
        cherrypy.engine.log(f'Adding refs/pull/*/head to repo {repo} config...')
        subprocess.check_output(
            ('git', *git_args, 'config', '--add', 'remote.origin.fetch',
             '+refs/pull/*/head:refs/pull/origin/*')
        )
        cherrypy.engine.log(f'Adding refs/pull/*/merge to repo {repo} config...')
        subprocess.check_output(
            ('git', *git_args, 'config', '--add', 'remote.origin.fetch',
             '+refs/pull/*/merge:refs/pull/origin/*')
        )

    cherrypy.engine.log(f'Fetching repo {repo}...')
    subprocess.check_output(
        ('git', *git_args, 'fetch', '--all')
    )


def test_repo(repo_slug, local_repo, pr):
    cherrypy.engine.log(f'Starting to test {pr} in repo {repo_slug}...')
