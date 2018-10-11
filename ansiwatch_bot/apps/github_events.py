import logging

import cherrypy

from .. import tools
from ..utils import bus_log


@cherrypy.tools.json_in()
@cherrypy.tools.json_to_args()
class GitHubEventHandlerApp:
    @cherrypy.expose
    def check_run(self, action, check_run, requested_action):
        check_run_conclusion = check_run['conclusion']
        check_run_name = check_run['name']
        check_suite_id = check_run['check_suite']['id']
        requested_action_identifier = (
            requested_action['identifier']
        )

        action_msg = ' '.join(map(str, [
            'Processing check run action', action,
            'with name', check_run_name,
            'with conclusion', check_run_conclusion,
            'from check suite id', check_suite_id,
            'and requested action identifier is',
            requested_action_identifier,
        ]))
        bus_log(action_msg, logging.INFO)

        return action_msg

    @cherrypy.expose
    def check_suite(self, action, check_suite):
        check_suite_head_branch = check_suite['head_branch']
        check_suite_head_sha = check_suite['head_sha']
        check_suite_status = check_suite['status']
        check_suite_conclusion = check_suite['conclusion']
        check_suite_url = check_suite['url']
        check_suite_pull_requests = check_suite['pull_requests']

        action_msg = ' '.join(map(str, [
            'Processing check suite action', action,
            'with head branch', check_suite_head_branch,
            'with head sha', check_suite_head_sha,
            'with status', check_suite_status,
            'with conclusion', check_suite_conclusion,
            'with URL', check_suite_url,
            'with PRs', check_suite_pull_requests,
        ]))
        bus_log(action_msg, logging.INFO)

        return action_msg

    @cherrypy.expose('integration_installation')
    def installation(self, action, installation, sender, repositories=None):
        installation_id = installation['id']

        action_msg = ' '.join(map(str, [
            'Processing installation action', action,
            'with ID', installation_id,
            'by', sender['login'],
        ]))
        bus_log(action_msg, logging.INFO)

        return action_msg

    @cherrypy.expose('integration_installation_repositories')
    def installation_repositories(
        self, action, installation,
        repositories_added, repositories_removed,
        repository_selection, sender,
    ):
        installation_id = installation['id']

        action_msg = ' '.join(map(str, [
            'Processing installation repositories action', action,
            'with ID', installation_id,
            'by', sender['login'],
        ]))
        bus_log(action_msg, logging.INFO)

        return action_msg


    @cherrypy.expose
    def ping(self, hook, hook_id, zen):
        app_id = hook['app_id']

        action_msg = ' '.join(map(str, [
            'Processing ping for App ID', app_id,
            'with ID', hook_id,
            'sharing Zen', zen,
        ]))

        bus_log(action_msg, logging.INFO)
        return action_msg
        # raise cherrypy.HTTPError(204, zen)
