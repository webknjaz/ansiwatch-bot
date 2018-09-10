ansiwatch-bot
-------------

Ansible content linter bot

Creating an openshift app
=========================

.. code:: bash

    oc new-project ansiwatch-bot
    oc new-app --env-file=.env openshift.yaml

Checking status
===============

.. code:: bash

    oc logs -f bc/ansiwatch-deployment

Destroying everything back
==========================

.. code:: bash

    oc delete all -l app=ansiwatch-deployment; oc delete secret ansiwatch-deployment
