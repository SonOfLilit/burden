======
Burden
======

Burden is a chore-management application written by Aur Saraf.


Structure
=========

Burden is made of a few apps:

hr
--

Manage organizations and workers (together known as "bodies") and their traits.

design
------

Define types of chores and rules for who can perform them.

schedule
--------

Define work schedules -- how many of each chore are needed when.

market
------

Assign and trade chores between bodies.

supermarket
-----------

UI for workers to trade chores.

resources
---------

Assign chores to bodies trying to distribute fairly.


IT
==

local_apps
----------

All these apps are stored in the `local_apps` directory, and we'd like
to include them like `import hr.models` etc'. So `manage.py` adds the
`local_apps` directory to `sys.path`.