from jira import JIRA
from jira.exceptions import JIRAError
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

user = 'candy@opswat.com'
apikey = 'QCMdjEnrBefZ0RpETly1AEE9'
server = 'https://opswat.atlassian.net'
jql = 'project = TEST AND comment ~ "release update" AND updated >= -1d'
from_email='candy_twilio@example.com'
to_emails='lxc1209@gmail.com'
subject='products release date have been updated'
LOG_FILENAME = "log.txt"


def authJIRA(user,apikey,server):
    options = {}
    options['server'] = server
    try:
        jira = JIRA (options, basic_auth=(user,apikey))
        return jira
    except JIRAError as e:
        if e.status_code == 401:
            logger.error("JIRA login failed, error code is: "+str(e.status_code))
    return None
        
def createDictFromJiraSearch(jira,jql):
    issues_in_proj = jira.search_issues(jql)
    if issues_in_proj:
        emailContent = {}
        for issue in issues_in_proj:
            issue = jira.issue(issue.key)
            summary = issue.fields.summary
            comments = issue.fields.comment.comments
            for comment in comments:
                emailContent[summary] = comment.body            
    else:
        emailContent = "No release update"
        logger.info("email content is: "+emailContent)
    return emailContent

def createHTMLFromDict(dictionary):
    html = """<html><table border="1">
    <tr><th>Product Release</th><th>Updates</th></tr>"""    
    for release in dictionary:
        html += "<tr><td>{}</td>".format(release)
        html += "<td>{}</td>".format(dictionary[release])
        html += "</tr>"
    html += "</table></html>"
    logger.debug("html content is: "+html)
    return html

def sendEmail(from_email,to_emails,subject,html):
    message = Mail(
        from_email = from_email,
        to_emails = to_emails,
        subject = subject,
        html_content=html)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        logger.info("sendgrid response code is: "+str(response.status_code))
        logger.debug(response.headers)
        logger.debug(response.body)
    except Exception as e:
        logger.error("fail to send email, error message is: "+e.message)
    return None

def configLogging(LOG_FILENAME):
    logger = logging.getLogger("Logging")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    fh = logging.FileHandler(LOG_FILENAME)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


 
logger = configLogging(LOG_FILENAME)
def main():
    jira = authJIRA(user,apikey,server)
    emailContent = createDictFromJiraSearch(jira,jql)
    if emailContent == "No release update":
        html = emailContent
    else:
        html = createHTMLFromDict(emailContent)
    sendEmail(from_email,to_emails,subject,html)

if __name__ == "__main__":
    main()
