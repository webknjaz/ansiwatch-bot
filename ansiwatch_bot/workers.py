import subprocess

import cherrypy


GITHUB_REPO_URL_TMPL = 'git://github.com/{slug}.git'


def sync_repo(repo, path):
    cherrypy.engine.log(f'Starting to sync repo {repo}...')
    if not (path / '.git').exists():
        cherrypy.engine.log(f'Cloning repo {repo}...')
        subprocess.check_output(
            ('git', 'clone', GITHUB_REPO_URL_TMPL.format(slug=repo), path)
        )
        cherrypy.engine.log(f'Adding refs/pull/*/head to repo {repo} config...')
        subprocess.check_output(
            ('git', '-C', str(path), 'config', '--add', 'remote.origin.fetch',
             '+refs/pull/*/head:refs/pull/origin/*')
        )
        cherrypy.engine.log(f'Adding refs/pull/*/merge to repo {repo} config...')
        subprocess.check_output(
            ('git', '-C', str(path), 'config', '--add', 'remote.origin.fetch',
             '+refs/pull/*/merge:refs/pull/origin/*')
        )

    cherrypy.engine.log(f'Fetching repo {repo}...')
    subprocess.check_output(
        ('git', '-C', str(path), 'fetch', '--all')
    )
