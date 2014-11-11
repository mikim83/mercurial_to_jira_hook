#coding: utf-8

#OJO! hemos modificado el dichero /data/hg/cgi-bin/hgweb.cgi para que este import funcione.
from jira.client import JIRA
import re
import urllib2
import json
import base64
import syslog



#If the hook returns True - hook fails
BAD_COMMIT = True
OK = False
MERCURIAL_HOST = "http://mercurialserver.example.com"
MERCURIAL_REPO = "reponame"
JIRA_HOST = "http://jiraserver.example.com"
JIRA_USER = "jiramercurialuser"
JIRA_PASSWORD = "UltraSecretPassword"
JIRA_SUPERUSERS = [ "admin1", "admin2", "admin3" ]
AK_47="""

                          .-----------------TTTT_-----_______
                        /''''''''''(______O] ----------____  \______/]_
     __...---'\"\"\"\_ --''   Q                               ___________@
 |'''                   ._   _______________=---------"\"\"\"\"\"\"
 |                ..--''|   l L |_l   |
 |          ..--''      .  /-___j '   '
 |    ..--''           /  ,       '   '
 |--''                /           `    \\
                      L__'         \    -
                                    -    '-.
                                     '.    /
                                       '-./

Script courtesy of the ISIS Python Sysadmin Crew
Join us!!
ALLAHU AKBAR!!!
	"""


def connect_jira(jira_server, jira_user, jira_password,ui):
    """
    Connect to JIRA. Return None on error
    """
    try:
        syslog.syslog("Connecting to JIRA: %s" % jira_server)
        jira_options = {'server': jira_server}
        jira = JIRA(options=jira_options,
                    # Note the tuple
                    basic_auth=(jira_user,
                                jira_password))
        return jira
    except Exception,e:
        syslog.syslog("Failed to connect to JIRA: %s" % e)
        ui.warn('=====\n')
        ui.warn("Failed to connect to JIRA: %s \n" % e)
        ui.warn('=====\n')
        return None



def checkCommitMessage(ui, repo, **kwargs):
    """Checks commit message for matching commit rule:
    Every commit message must include JIRA issue key
    Example:
    Fixed world creation
    PRJ-42 - added meaning of life

    Include this hook in .hg/hgrc

    [hooks]
    pretxncommit.jirakeycheck = python:/path/jirakeycheck.py:checkCommitMessage
    """
    syslog.syslog('Entering in checkCommitMessage')

    hg_commit_message = repo['tip'].description()
    if checkMessage(hg_commit_message,ui) is False:
        printUsage(ui)
        #reject commit transaction
        return BAD_COMMIT
    else:
        jclient = connect_jira(JIRA_HOST, JIRA_USER, JIRA_PASSWORD,ui)
        p = re.compile('\w+-\d+')
        res = p.findall(hg_commit_message)
        for match in res:
                syslog.syslog(match)
                commentkey=match
                syslog.syslog(repo['tip'].user().split(' ', 1)[0])
		commentuser=repo['tip'].user().split(' ', 1)[0]
		syslog.syslog(repo['tip'].description())
                commentcomment=repo['tip'].description()
                jclient.add_comment(commentkey, "COMMIT de "+commentuser+"\\"+commentcomment)

        return OK




def checkCreateBranch(ui, repo, **kwargs):
    """Checks create branch for matching naming rule:
    Every branch must include JIRA issue key
    Example:
    PRJ-42 - added meaning of life

    Include this hook in .hg/hgrc

    [hooks]
    pretxncommit.jirakeycheck = python:/path/jirakeycheck.py:checkCreateBranch
    """
    syslog.syslog('Entering in checkCreateBranch')
    hg_branch_name = repo['tip'].branch()
    if repo['tip'].user().split(' ', 1)[0] not in JIRA_SUPERUSERS:
        if checkBranch(hg_branch_name,ui) is False:
            printUsage(ui)
            #reject commit transaction
            return BAD_COMMIT
        else:
            return OK
    else:
        return OK


def checkAllCommitMessage(ui, repo, node, **kwargs):
    """
    For pull: checks commit messages for all incoming commits
    It is good for master repo, when you pull a banch of commits

    [hooks]
    pretxnchangegroup.jirakeycheckall =
        python:/path/jirakeycheck.py:checkAllCommitMessage
    """
    syslog.syslog('Entering in checkAllCommitMessage')
    for rev in xrange(repo[node].rev(), len(repo)):
        message = repo[rev].description()
        if checkMessage(message,ui) is False:
            ui.warn(
                "Revision "
                + str(rev)
                + " commit message:["
                + message
                + "] | JIRA issue key is not set or not found\n"
            )
            printUsage(ui)
            #reject
            return BAD_COMMIT
    return OK


def checkAllCreateBranch(ui, repo, node, **kwargs):
    """
    For pull: checks commit messages for all incoming commits
    It is good for master repo, when you pull a banch of commits

    [hooks]
    pretxnchangegroup.jirakeycheckall =
        python:/path/jirakeycheck.py:checkAllCreateBranch
    """
    syslog.syslog('Entering in checkAllCreateBranch')
    for rev in xrange(repo[node].rev(), len(repo)):
        if repo[rev].user().split(' ', 1)[0] not in JIRA_SUPERUSERS:
            syslog.syslog('User commit from: %s' % repo[rev].user().split(' ', 1)[0])
            branch = repo[rev].branch()
            if checkBranch(branch,ui) is False:
                ui.warn(
                    "Revision "
                    + str(rev)
                    + " Branch Name:["
                    + branch
                    + "] | JIRA issue key is not set or not found on branch name\n"
                )
                printUsage(ui)
                #reject
                syslog.syslog('User %s can not commit with branch name: %s ' % (repo[rev].user().split(' ', 1)[0],repo[rev].branch()))
                return BAD_COMMIT
            else:
                jclient = connect_jira(JIRA_HOST, JIRA_USER, JIRA_PASSWORD,ui)
		p = re.compile('\w+-\d+')
                res = p.findall(repo[rev].branch())
		for match in res:
                    syslog.syslog(match)
                    commentkey=match
                    commentuser=repo[rev].user().split(' ', 1)[0]
                    commentcomment=repo[rev].description()
                    commentrevision=str(rev)
                    commentfiles=repo[rev].files()
		    commentbody="""
				{panel:title=COMMIT de [~%s]|borderStyle=solid|borderColor=#141414|titleBGColor=#c3d8d8|bgColor=#eee0f6}
                                Comentario:
                                {quote}%s{quote}
                                Revisión: [%s|%s/repos/%s/rev/%s]
                                Ficheros:
				""" % (commentuser,commentcomment,commentrevision,MERCURIAL_HOST,MERCURIAL_REPO,commentrevision)
                    i=0
                    extrafiles=0
                    for file in commentfiles:
                        i += 1
                        if (i<4):
                            commentbody=commentbody+"""* [%s|%s/repos/%s/comparison/%s/%s]
                                                    """ % (file,MERCURIAL_HOST,MERCURIAL_REPO,commentrevision,file)
                        else:
                            i += 1
                            extrafiles += 1
                    if (extrafiles>0):
                        commentbody=commentbody+"""* ... y [%d|%s/repos/%MERCURIAL_REPO/file/%s] ficheros mas.""" % (extrafiles,MERCURIAL_HOST,MERCURIAL_REPO,commentrevision)

                    commentbody=commentbody+"""{panel}"""
                    jclient.add_comment(commentkey, commentbody)
                return OK

        else:
            syslog.syslog('User %s entering in admin mode for branch name: %s' % (repo[rev].user().split(' ', 1)[0],repo[rev].branch()))
            ui.status('=====\n')
            ui.status('You have super admin rights\n')
            ui.status('Remember, With great power comes great responsibility\n')
            ui.status(AK_47)
            ui.status('\n=====\n')
            jclient = connect_jira(JIRA_HOST, JIRA_USER, JIRA_PASSWORD,ui)
            p = re.compile('\w+-\d+')
            res = p.findall(repo[rev].branch())
            for match in res:
                commentkey=match
                commentuser=repo[rev].user().split(' ', 1)[0]
                commentcomment=repo[rev].description()
                commentrevision=str(rev)
                commentfiles=repo[rev].files()
                commentbody="""
			{panel:title=COMMIT de [~%s]|borderStyle=solid|borderColor=#141414|titleBGColor=#c3d8d8|bgColor=#eee0f6}
                        Comentario:
                        {quote}%s{quote}
                        Revisión: [%s|%s/repos/%s/rev/%s]
                        Ficheros:
		        """ % (commentuser,commentcomment,commentrevision,MERCURIAL_HOST,MERCURIAL_REPO,commentrevision)
                i=0
                extrafiles=0
                for file in commentfiles:
                    i += 1
                    if (i<4):
                        commentbody=commentbody+"""* [%s|%s/repos/%s/comparison/%s/%s]
                                                """ % (file,MERCURIAL_HOST,MERCURIAL_REPO,commentrevision,file)
                    else:
                        i += 1
                        extrafiles += 1
                if (extrafiles>0):
                    commentbody=commentbody+"""* ... y [%d|%s/repos/%s/file/%s] ficheros mas.""" % (extrafiles,MERCURIAL_HOST,MERCURIAL_REPO,commentrevision)

                commentbody=commentbody+"""{panel}"""
                jclient.add_comment(commentkey, commentbody)
            return OK
    return OK


def checkMessage(msg,ui):
    """
    Checks message for matching regex

    Correct message example:
    PRJ-123 - your commit message here

    #"PRJ-123" is necessary prefix here
    """


    is_correct = False

    p = re.compile('\w+-\d+')
    res = p.findall(msg)
    for match in res:
        req = urllib2.Request(JIRA_HOST+"/rest/api/2/search?jql=key="+match)
	base64string = base64.encodestring('%s:%s' % (JIRA_USER, JIRA_PASSWORD)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
        req.add_header("Content-Type", "application/json")
        try:
           result = urllib2.urlopen(req)
        except urllib2.HTTPError, err:
           if err.code == 400:
              #print ("Error %d: Issue not found, try again.") % err.code
              ui.warn ("Error "+str(err.code)+": Jira Issue not found in commit message, on: "+JIRA_HOST+"/rest/api/2/search?jql=key="+match+".\n")
           elif err.code == 404:
              #print ("Error %d: JIRA Host is weird. Do I have access to the API?") % err.code
              ui.warn("Error "+str(err.code)+": JIRA Host is weird. Do I have access to the API?\n")
           else:
              #print ("Error %d: You have fail at failing.") % err.code
              ui.warn("Error "+str(err.code)+": You have fail at failing.\n")
           #raise SystemExit
           is_correct = False
           return is_correct

        except urllib2.URLError, err:
            print "ERROR: JIRA Host not found"
            ui.warn("Error JIRA host not found or incorrect.\n")
            is_correct = False
            return is_correct

        jsondict = json.load(result.fp)
        if match in jsondict["issues"][0]["key"]:
             is_correct = True
        else:
             is_correct = False
        result.close()

    return is_correct


def checkBranch(msg,ui):
    """
    Checks branch name for matching regex

    Correct message example:
    PRJ-123 - your commit message here

    #"PRJ-123" is necessary prefix here
    """


    is_correct = False

    p = re.compile('\w+-\d+')
    res = p.findall(msg)
    for match in res:
        req = urllib2.Request(JIRA_HOST+"/rest/api/2/search?jql=key="+match)
	base64string = base64.encodestring('%s:%s' % (JIRA_USER, JIRA_PASSWORD)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
        req.add_header("Content-Type", "application/json")
        try:
           result = urllib2.urlopen(req)
        except urllib2.HTTPError, err:
           if err.code == 400:
              #print ("Error %d: Issue not found, try again.") % err.code
              ui.warn ("Error "+str(err.code)+": Jira Issue not found in branch name, on: "+JIRA_HOST+"/rest/api/2/search?jql=key="+match+".\n")
           elif err.code == 404:
              #print ("Error %d: JIRA Host is weird. Do I have access to the API?") % err.code
              ui.warn("Error "+str(err.code)+": JIRA Host is weird. Do I have access to the API?\n")
           else:
              #print ("Error %d: You have fail at failing.") % err.code
              ui.warn("Error "+str(err.code)+": You have fail at failing.\n")
           #raise SystemExit
           is_correct = False
           return is_correct

        except urllib2.URLError, err:
            print "ERROR: JIRA Host not found"
            ui.warn("Error JIRA host not found or incorrect.\n")
            is_correct = False
            return is_correct

	jsondict = json.load(result.fp)
        if match in jsondict["issues"][0]["key"]:
             is_correct = True
        else:
             is_correct = False
        result.close()

    return is_correct




def printUsage(ui):
    ui.warn('=====\n')
    ui.warn('Branch name must have JIRA issue key\n')
    ui.warn('Example:\n')
    ui.warn('TBP-42 - the answer to life, universe and everything \n')
    ui.warn('=====\n')
