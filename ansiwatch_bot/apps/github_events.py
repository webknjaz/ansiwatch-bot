import logging

import cherrypy

from ..utils import bus_log


def get_request_json():
    return cherrypy.request.json


@cherrypy.tools.json_in()
class GitHubEventHandlerApp:
    @cherrypy.expose
    def check_run(self):
        event_data = get_request_json()
        action = event_data['action']
        check_run = event_data['check_run']
        check_run_conclusion = check_run['conclusion']
        check_run_name = check_run['name']
        check_suite_id = check_run['check_suite']['id']
        requested_action_identifier = (
            event_data['requested_action']['identifier']
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
    def check_suite(self):
        event_data = get_request_json()
        action = event_data['action']
        check_suite = event_data['check_suite']
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

    @cherrypy.expose
    def ping(self):
        event_data = get_request_json()
        app_id = event_data['hook']['app_id']
        zen = event_data['zen']
        bus_log(f'App ID: {app_id}', logging.INFO)
        bus_log(f'Zen: {zen}', logging.INFO)
        return zen
        # raise cherrypy.HTTPError(204, zen)
