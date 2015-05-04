import requests
import xml.etree.ElementTree as ET
import time

API_KEY='xx'
RUNDECKSERVER = 'http://127.0.0.1'
RUNDECKPORT='80'
EXPIRE_DAYS = 20
TODAY = int(round(time.time() * 1000))
EXPIRE_MILISECONDS = EXPIRE_DAYS * 24 * 60 * 60 * 1000


# API call to get the list of the existing projects on the server.
def listProjects():
    url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/1/projects'
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.get(url, headers=headers, verify=False)
    return r.text
    
# Returns list of all the project names
def getProjectNames(projectsinfo_xml):
    project_names = []
    root = ET.fromstring(projectsinfo_xml)
    for projects in root:	
        for name in projects.findall('project'):
            project_names.append(name.find('name').text)
    return project_names   

# API call to get the list of the jobs that exist for a project.
def listJobsForProject(project_mame):
    url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/1/jobs'
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
    url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/1/job/'+job_id+'/executions'
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
    url =  RUNDECKSERVER +':'+RUNDECKPORT+'/api/12/execution/'+execution_id
    headers = {'Content-Type': 'application/json','X-RunDeck-Auth-Token': API_KEY }
    r = requests.delete(url, headers=headers, verify=False)    

def isOlderThanExpireDays(execution_date, today):
    if ((today - execution_date) > EXPIRE_MILISECONDS):
        return True
    return False

def checkDeletion(execid_dates):
    for exec_id, exec_date in execid_dates.iteritems():
        if isOlderThanExpireDays(int(exec_date), TODAY):
    	    deleteExecution(exec_id)

projects = getProjectNames(listProjects())
for project in projects:
    print 'project:\t'+project
    jobids = getJobIDs(listJobsForProject(project))
    for jobid in jobids:
        print '\tjobid:\t'+jobid
        checkDeletion(getExecutionDate(getExecutionsForAJob(jobid))) 
