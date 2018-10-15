from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory

import cherrypy
from cherrypy.process.plugins import Monitor, SimplePlugin

from .workers import sync_repo, test_repo


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
        self.bus.log(f'Synching {repo} to {tmp_repo_path}...')
        mon = ConfigurableMonitor(
            self.bus, sync_repo,
            kwargs={
                'repo': repo,
                'path': Path(tmp_repo_path.name),
            },
            frequency=20, name=f'{repo}-sync',
        )
        mon.subscribe()
        mon.start()

        self.repo_monitors[repo] = tmp_repo_path, mon
        del mon

    def wipe_repo(self, repo):
        self.bus.log(f'Got asked to wipe out {repo}...')
        if repo not in self.repo_monitors:
            self.bus.log(f'{repo} is not on the list')
            return

        self.bus.log(f'Wiping {repo} out')
        tmp_repo_path, mon = self.repo_monitors.pop(repo)

        mon.stop()
        mon.unsubscribe()

        del mon

        tmp_repo_path.cleanup()
        del tmp_repo_path

        self.bus.log(f'{repo} has been cleaned up successfully')

    def _cleanup(self):
        for r in list(self.repo_monitors.keys()):
            self.wipe_repo(r)

    def test_pr(self, repo, pr):
        self.bus.log(f'Got asked to test {repo}, PR {pr}...')
        local_repo_wd = self.repo_monitors[repo]
        test_repo(repo, local_repo_wd, pr)


def subscribe_all():
    cherrypy.engine.repo_sync = RepoSyncPlugin(cherrypy.engine)
    cherrypy.engine.repo_sync.subscribe()
