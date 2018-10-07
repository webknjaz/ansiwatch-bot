ansiwatch-bot
-------------

Ansible content linter bot

Creating an openshift app
=========================

.. code:: bash

    oc new-project ansiwatch-bot
    oc new-app --param-file=.env openshift.yaml

Triggering build
================

.. code:: bash

    oc start-build ansiwatch-bot

Triggering deployment
=====================

.. code:: bash

    oc rollout latest ansiwatch-bot

Triggering automatic deployment
===============================

1. From the ``Web Console`` homepage, navigate
   to project ``ansiwatch-bot``
2. Click on ``Browse > Builds``
3. Click the link with ``BuildConfig`` named ``ansiwatch-bot``
4. Click the ``Configuration`` tab
5. Click the "``Copy to clipboard``" icon to the right of
   the "``GitHub webhook URL``" field
6. Navigate to your repository on GitHub and click
   on ``repository settings > webhooks > Add webhook``
7. Paste your webhook URL provided by OpenShift in
   the "``Payload URL``" field
8. Change the "``Content type``" to '``application/json``'
9. Leave the defaults for the remaining fields — that's it!

After you save your webhook, if you refresh your settings page
you can see the status of the ping that Github sent to OpenShift
to verify it can reach the server.

Note: adding a webhook requires your OpenShift server
to be reachable from GitHub.

Now, whenever you push to that repo it will trigger deployment
in OpenShift.

Checking status
===============

.. code:: bash

    oc logs -f bc/ansiwatch-bot

Destroying everything back
==========================

.. code:: bash

    oc delete all -l app=ansiwatch-bot; oc delete secret ansiwatch-bot
