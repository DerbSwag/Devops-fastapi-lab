#!/bin/bash
JENKINS=http://localhost:32080
AUTH="admin:YJmyaScUnYJZfdWQExHs3U"

CRUMB=$(curl -s -u $AUTH "$JENKINS/crumbIssuer/api/json" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["crumbRequestField"]+":"+d["crumb"])')
echo "Crumb: $CRUMB"

# Update pipeline config
HTTP_CODE=$(curl -s -u $AUTH -X POST "$JENKINS/job/fastapi-pipeline/config.xml" \
  -H "Content-Type: application/xml" \
  -H "$CRUMB" \
  -d '<?xml version="1.0" encoding="UTF-8"?><flow-definition plugin="workflow-job"><definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps"><scm class="hudson.plugins.git.GitSCM" plugin="git"><configVersion>2</configVersion><userRemoteConfigs><hudson.plugins.git.UserRemoteConfig><url>https://github.com/DerbSwag/Devops-fastapi-lab.git</url></hudson.plugins.git.UserRemoteConfig></userRemoteConfigs><branches><hudson.plugins.git.BranchSpec><name>*/main</name></hudson.plugins.git.BranchSpec></branches></scm><scriptPath>Jenkinsfile</scriptPath><lightweight>true</lightweight></definition></flow-definition>' \
  -o /dev/null -w '%{http_code}')
echo "Config update: $HTTP_CODE"

# Trigger build
HTTP_CODE=$(curl -s -u $AUTH -X POST "$JENKINS/job/fastapi-pipeline/build" \
  -H "$CRUMB" -o /dev/null -w '%{http_code}')
echo "Build trigger: $HTTP_CODE"
