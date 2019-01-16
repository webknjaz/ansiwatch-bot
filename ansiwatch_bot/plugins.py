from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory

from check_in.github_api import GithubClient
import cherrypy
from cherrypy.process.plugins import Monitor, SimplePlugin
import github
import requests

from .config import APP_ID, PRIVATE_KEY, USER_AGENT
from .workers import sync_repo, test_repo


class GithubWrapper(GithubClient):
    def __init__(self, github_client, repo_slug=None, user_agent=None):
        self._gh_client = github_client
        self._repo_slug = repo_slug
        self._check_runs_base_uri = f'/repos/{repo_slug}/check-runs'
        self.user_agent = user_agent


class ConfigurableMonitor(Monitor):
    """A classic monitor plugin with args."""
    args = []
    """Positional args for the callback function."""

    kwargs = {}
    """Keyword args for the callback function."""

    def __init__(
        self, bus, callback,
        *,
        args=None, kwargs=None,
        frequency=60, name=None,
    ):
        super().__init__(
            bus=bus, callback=callback,
            frequency=frequency, name=name,
        )

        if args is not None:
            self.args = args
        if kwargs is not None:
            self.kwargs = kwargs

        self.callback = partial(
            self.callback,
            *self.args,
            **self.kwargs,
        )


class RepoSyncPlugin(SimplePlugin):

    def __init__(self, bus):
        super().__init__(bus)
        self.repo_monitors = {}

    def start(self):
        self.bus.log('Starting repo sync plugin')
        self.bus.subscribe('repo-sync', self.sync_repo)
        self.bus.subscribe('repo-wipe', self.wipe_repo)
        self.bus.subscribe('repo-test-pr', self.test_pr)

    def stop(self):
        self.bus.log('Stopping repo sync plugin')
        self.bus.unsubscribe('repo-sync', self.sync_repo)
        self.bus.unsubscribe('repo-wipe', self.wipe_repo)
        self._cleanup()

    def sync_repo(self, repo):
        self.bus.log(f'Got asked to sync {repo}...')
        if repo in self.repo_monitors:
            self.bus.log(f'{repo} is already being synched...')
            return

        tmp_dir = TemporaryDirectory(
            prefix=f'ansiwatch_bot--{repo.replace("/", "--")}--',
        )
        tmp_repo_path = Path(tmp_dir.name) / 'repo'
        self.bus.log(f'Synching {repo} to {tmp_repo_path}...')
        mon = ConfigurableMonitor(
            self.bus, sync_repo,
            kwargs={
                'repo': repo,
                'path': tmp_repo_path,
            },
            frequency=20, name=f'{repo}-sync',
        )
        mon.subscribe()
        mon.start()

        self.repo_monitors[repo] = tmp_dir, tmp_repo_path, mon
        del mon

    def wipe_repo(self, repo):
        self.bus.log(f'Got asked to wipe out {repo}...')
        if repo not in self.repo_monitors:
            self.bus.log(f'{repo} is not on the list')
            return

        self.bus.log(f'Wiping {repo} out')
        tmp_dir, _, mon = self.repo_monitors.pop(repo)

        mon.stop()
        mon.unsubscribe()

        del mon

        tmp_dir.cleanup()
        del tmp_dir

        self.bus.log(f'{repo} has been cleaned up successfully')

    def _cleanup(self):
        for r in list(self.repo_monitors.keys()):
            self.wipe_repo(r)

    def test_pr(self, repo, pr):
        self.bus.log(f'Got asked to test {repo}, PR {pr}...')
        local_repo_wd = self.repo_monitors[repo][1]
        test_repo(repo, local_repo_wd, pr)


class GithubAppInstallationsPlugin(SimplePlugin):

    def __init__(self, bus, app_id, private_key, user_agent):
        super().__init__(bus)

        self._app_id = app_id
        self._private_key = private_key
        self._user_agent = user_agent

        self.installations = {}
        self.installation_clients = {}
        self.repo_to_installation = {}

        self._gh_integration = github.GithubIntegration(
            self._app_id,
            self._private_key,
        )

    def get_all_installations(self):
        accept_header = 'application/vnd.github.machine-man-preview+json'
        jwt = self._gh_integration.create_jwt()
        response = requests.post(
            'https://api.github.com/app/installations',
            headers={
                'Authorization': f'Bearer {jwt}',
                'Accept': accept_header,
                'User-Agent': self._user_agent,
            },
        )
        for install in response.json():
            self.bus.log(f'Got {install!r}')
            install_token = (
                self._gh_integration.get_access_token(install['id']).token
            )
            inst_resp = requests.post(
                'https://api.github.com/installation/repositories',
                headers={
                    'Authorization': f'token {install_token}',
                    'Accept': accept_header,
                    'User-Agent': self._user_agent,
                },
            )
            gh_repos = inst_resp['repositories']
            self.add_installation(install, gh_repos)

    def start(self):
        self.bus.log('Starting GitHub App Installations plugin')
        self.bus.log('Retrieving all GitHub App Installations')
        self.get_all_installations()
        self.bus.log('Subscribing GitHub App Installation actions')
        self.bus.subscribe('gh-installation-add', self.add_installation)
        self.bus.subscribe('gh-installation-rm', self.rm_installation)
        self.bus.subscribe('gh-installation-post-check', self.post_check)
        self.bus.subscribe('gh-installation-update-check', self.update_check)

    def stop(self):
        self.bus.log('Stopping GitHub App Installations plugin')
        self.bus.unsubscribe('gh-installation-add', self.add_installation)
        self.bus.unsubscribe('gh-installation-rm', self.rm_installation)
        self.bus.unsubscribe('gh-installation-post-check', self.post_check)
        self.bus.unsubscribe('gh-installation-update-check', self.update_check)

    def add_installation(self, gh_installation, gh_repos):
        install_id = gh_installation['id']

        self.installations[install_id] = gh_installation
        self.installation_clients[install_id] = github.Github(
            self._gh_integration.get_access_token(install_id).token
        )

        for repo in gh_repos:
            self.repo_to_installation[repo['full_name']] = install_id

    def rm_installation(self, install_id):
        if install_id not in self.installations:
            self.bus.log(f'We do not have {install_id} saved...')
            return

        for repo in self.installations[install_id]:
            del self.repo_to_installation[repo['full_name']]

        del self.installations[install_id]
        del self.installation_clients[install_id]

    def post_check(self, repo_slug, head_branch, head_sha, req=None):
        if req is None:
            req = {}

        install_id = self.repo_to_installation[repo_slug]
        raw_gh_client = self.installation_clients[install_id]
        gh_client = GithubWrapper(
            github_client=raw_gh_client,
            repo_slug=repo_slug,
            user_agent=self._user_agent,
        )

        api_response = gh_client.post_check(head_branch, head_sha, req)

        self.bus.log(f"[post] Check Suite ID: {api_response['check_suite']['id']}")
        self.bus.log(f"[post] Check Run ID: {api_response['id']}")

        return api_response['id']

    def update_check(self, repo_slug, check_run_id, req=None):
        if req is None:
            req = {}

        install_id = self.repo_to_installation[repo_slug]
        raw_gh_client = self.installation_clients[install_id]
        gh_client = GithubWrapper(
            github_client=raw_gh_client,
            repo_slug=repo_slug,
            user_agent=self._user_agent,
        )

        api_response = gh_client.update_check(check_run_id, req)

        self.bus.log(f"[update] Check Suite ID: {api_response['check_suite']['id']}")
        self.bus.log(f"[update] Check Run ID: {api_response['id']}")


def subscribe_all():
    cherrypy.engine.repo_sync = RepoSyncPlugin(cherrypy.engine)
    cherrypy.engine.repo_sync.subscribe()

    cherrypy.engine.gh_app_installations = GithubAppInstallationsPlugin(
        cherrypy.engine, APP_ID,
        PRIVATE_KEY, USER_AGENT,
    )
    cherrypy.engine.gh_app_installations.subscribe()
