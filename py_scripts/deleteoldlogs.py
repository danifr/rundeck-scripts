import requests
import xml.etree.ElementTree as ET
import time

API_KEY='myAPIkeyfglIdHkIuRerDBPhgt'
PROJECT_NAME = 'Myproject'
RUNDECKSERVER = 'https://yourrundeckserver.com'

MILISECONDS_IN_THREE_MONTHS = 7889000000
TODAY = int(round(time.time() * 1000))

# API call to get the list of the jobs that exist for a project.
def listJobsForProject(project_mame):
    url = 'https://'+ RUNDECKSERVER +':4443/api/1/jobs'
    payload = { 'project':  project_mame }
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.get(url, params=payload, headers=headers, verify=False)
    return r.text

# Returns list of all the jobids
def getJobIDs(jobsinfo_xml):
    job_ids = []
    root = ET.fromstring(jobsinfo_xml)	
    for jobs in root:
        for job in jobs:
            job_ids.append(job.attrib['id'])
    return job_ids

# API call to get the list of the executions for a Job.      
def getExecutionsForAJob(job_id):
    url = 'https://'+ RUNDECKSERVER +':4443/api/1/job/'+job_id+'/executions'
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.get(url, headers=headers, verify=False)
    return r.text

# Returns a dict {'execution_id01': 'execution_date01', 'execution_id02': 'execution_date02', ... }
def getExecutionDate(executionsinfo_xml):
    execid_dates = {}
    root = ET.fromstring(executionsinfo_xml)
    for executions in root:     
        for execution in executions.findall('execution'):
            execution_id = execution.get('id')
            for date in execution.findall('date-ended'):
                execution_date = date.get('unixtime')
    	    execid_dates[execution_id] = execution_date
    return execid_dates
       
#API call to delete an execution by ID
def deleteExecution(execution_id):
    url = 'https://'+ RUNDECKSERVER +':4443/api/12/execution/'+execution_id
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.delete(url, headers=headers, verify=False)    

    
def isOlderThan90days(execution_date, today):
    if ((today - execution_date) > MILISECONDS_IN_THREE_MONTHS):
        return True
    return False

def check(execid_dates):
    for exec_id, exec_date in execid_dates.iteritems():
    	if isOlderThan90days (int(exec_date), TODAY):
    	    getExecutionDate(exec_id)
    	       
jobids = getJobIDs(listJobsForProject(PROJECT_NAME))
for jobid in jobids:
    check(getExecutionDate(getExecutionsForAJob(jobid)))
