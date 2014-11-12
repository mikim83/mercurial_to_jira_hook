mercurial_to_jira_hook
======================

based on https://github.com/johnner/mercurial-jira-commit-message-hook

This Mercurial hook adds comments extracted from commits to jira issues based on branch name.

Features
------------
1. Checks the newly created branch name against Jira server. If doesn't exitst, it blocks the push.
2. When pushing code, it checks the branch name againts Jira server. If the branch name doesn't have a valid Jira issue, the push is blocked.
3. Admin list of users that can create branches with any name (usefull for merging in default).


Pre-requisites
------------
1. Mercurial server with hgweb installed
2. Jira server with jsql activated ( It should work with v5.0 o superior)
3. Pyhton 2.6 or superior recomended
4. Jira python library installed on mercurial server
<div>
<pre>
	pip install jira
</pre>
</div>


Installation
------------
1. Copy `jirabranchcheck.py` to ~/.hg (or any dir you like)
2. Add the following lines to $HOME/.hgrc
<div>
<pre>

[hooks]
   pretxncommit.jirabranchcheck = python:~/.hg/jirabranchcheck.py:checkCreateBranch
   pretxnchangegroup.jirakeycheckall = python:~/.hg/jirabranchcheck.py:checkAllCreateBranch

</pre>
</div>
3. Set script variables `MERCURIAL_HOST`, `MERCURIAL_REPO_PATH`, `MERCURIAL_REPO`, `MERCURIAL_SUPERUSERS`, `JIRA_HOST`, `JIRA_USER`, `JIRA_PASSWORD` in jirabranchcheck.py
MERCURIAL variables are used to construct links to revsions, files, etc... Links are contructed this way: `MERCURIAL_HOST`/`MERCURIAL_REPO_PATH`/`MERCURIAL_REPO`


TODO
------------
1. Create exception for branches without jira issue on it´s name.
2. Add comments control. What if we also want a jira issue on the commit comment?
3. Rule the world
