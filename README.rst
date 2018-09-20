ansiwatch-bot
-------------

Ansible content linter bot

Creating an openshift app
=========================

.. code:: bash

    oc new-project ansiwatch-bot
    oc new-app --env-file=.env openshift.yaml

Triggering build
================

.. code:: bash

    oc start-build ansiwatch-bot

Checking status
===============

.. code:: bash

    oc logs -f bc/ansiwatch-bot

Destroying everything back
==========================

.. code:: bash

    oc delete all -l app=ansiwatch-bot; oc delete secret ansiwatch-bot
