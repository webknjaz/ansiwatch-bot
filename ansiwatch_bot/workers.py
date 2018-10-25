import datetime
import itertools
import pathlib
import subprocess

import cherrypy

from .utils import pub, separate_git_worktree


GITHUB_REPO_URL_TMPL = 'git://github.com/{slug}.git'


def get_git_separate_dir_args(path):
    path_str = str(path)
    # FIXME: replace with '-C' once Git supports it
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

    pr_branch = f'refs/pull/origin/{pr}'
    pr_branch_merge = f'refs/pull-merge/origin/{pr}'
    # TODO: maybe just HEAD?
    head_sha = subprocess.check_output(
        (*git_exec_cmd, 'rev-parse', pr_branch)
    ).decode().strip()
    base_req = {
        'name': 'ansible-review',
    }
    check_id = pub(
        'gh-installation-post-check', repo_slug=repo_slug,
        head_branch=pr_branch, head_sha=head_sha,
        req={'status': 'queued', **base_req},
        #req={'output': {'title': '', 'summary': ''}, **base_req},
    )

    git_diff_proc = subprocess.Popen(
        (*git_exec_cmd, 'diff', f'...{pr_branch}'),
        stdout=subprocess.PIPE,
    )
    pub(
        'gh-installation-update-check',
        repo_slug=repo_slug, check_run_id=check_id,
        req={'status': 'in_progress', **base_req},
    )
    # TODO: maybe s/pr_branch/head_sha/?
    with separate_git_worktree(local_repo, pr_branch) as tmp_repo:
        pub(
            'gh-installation-update-check',
            repo_slug=repo_slug, check_run_id=check_id,
            req={'status': 'in_progress', **base_req},
        )
        ansible_review_proc = subprocess.run(
            (pathlib.Path.cwd() / 'py2venv/bin/ansible-review', ),
            stdin=git_diff_proc.stdout,
            stdout=subprocess.PIPE,
            check=True,
            cwd=tmp_repo,
            shell=True,
        )
    pub(
        'gh-installation-update-check',
        repo_slug=repo_slug, check_run_id=check_id,
        req={
            'status': 'completed',
            'conclusion':
                'success' if ansible_review_proc.returncode == 0
                else 'failure',
            'completed_at':
                datetime.datetime.now().astimezone().isoformat(),
            **base_req,
        },
    )
    annotations = []
    warnings = []
    text_results = ansible_review_proc.stdout.decode().splitlines()
    for l in text_results:
        file_or_level, msg = l.split(': ')
        if file_or_level == 'WARN':
            cherrypy.engine.log(f'[ansible-review][WARNING]: {msg}')
            warnings.append(msg)
        else:
            file_name, line_num = file_or_level.split(':')
            line_num = int(line_num)
            error_code, error_comment = msg.split('] ')
            error_code = error_code[1:]
            cherrypy.engine.log(f'[ansible-review][ERROR]: {error_code} | {error_comment} | file={file_name} line={line_num}')

            annotations.append({
                'path': file_name,
                'start_line': line_num,
                'end_line': line_num,
                'annotation_level': 'failure',
                'message': f'{error_code}: {error_comment}',
                'title': 'ansible-review',
                'raw_details': l,
            })

    summary = ''
    if warnings:
        summary = '\n'.join(
            itertools.chain(
                ('Common warnings:', ),
                map(lambda w: '* ' + w, warnings),
            )
        )
    pub(
        'gh-installation-update-check',
        repo_slug=repo_slug, check_run_id=check_id,
        req={
            'output': {
                'title': 'Standards compliance',
                'summary': summary,
                'annotations': annotations,
            },
            **base_req,
        },
    )
