node("master") {
  stage("Update description") {
    setDescription("www.example.com")
  }
}

def branches = [:]

for (area in ['area1', 'area2', 'area3']) {
  String currentArea = area;

  branches[area] = {
    node {
      stage("Build ${currentArea}") {
      }
      stage("Deploy ${currentArea}") {
      }
    }
  }
}

parallel branches

@NonCPS
def setDescription(baseDomain) {
  def branch = BRANCH_NAME
  def feature_name = (branch =~ /^feature-/) ? branch.substring(8) : "develop"
  def links = ""
  for (area in ['area1', 'area2', 'area3']) {
    if (feature_name == "develop") {
      // _target="blank" doesn't work in Jenkins
      links += "${area}: <a href=\"https://${area}-${baseDomain}\">${area}-${baseDomain}</a><br>\n";
    }else {
      links += "${area}: <a href=\"https://${feature_name}-${area}-${baseDomain}\">${feature_name}-${area}-${baseDomain}</a><br>\n";
    }
  }

  def job_item = Jenkins.instance.getItemByFullName(env.JOB_NAME)
  job_item.setDescription("Links on result:<br>\n${links}")
  job_item.save()
}
