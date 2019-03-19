/* Jenkins Extended Choice Example to:
   1) access secrets from Parameters Groovy Script
   2) list s3 and Gcloud buckets
   3) intersect version (don't forget tokenize vs split)
*/


def s3_bucket = "s3://project_s3_staging/"
def gc_bucket = "gs://project_gcloud_staging/"

import com.cloudbees.plugins.credentials.CredentialsProvider;
import com.cloudbees.plugins.credentials.common.StandardCredentials
import jenkins.model.Jenkins;

def creds = CredentialsProvider.lookupCredentials(
    StandardCredentials.class,
    Jenkins.instance
);

def c = creds.findResult { it.id == 's3_access_key' ? it : null }
def s3_access_key = c.getSecret()

def c2 = creds.findResult { it.id == 's3_secret_key' ? it : null }
def s3_secret_key = c2.getSecret()

def s3_versions_list = []
try {
  def s3_command = "s3cmd --access_key=${s3_access_key} --secret_key=${s3_secret_key} ls ${s3_bucket}"
  def filter_command = "awk '{ print \$2 }' | xargs basename -a | egrep '^v'"
  def s3_list = ["sh", "-c", "${s3_command} | ${filter_command}"].execute().text
  s3_versions_list = "${s3_list}".tokenize('\n')
} catch (Exception e) {
  return ["Error s3cmd", e]
}

def gcloud_versions_list =  []

try {
  def shell_command = "gsutil ls -d ${gc_bucket}"
  def filter_command = "xargs basename -a | egrep '^v'"
  def versions = ["sh", "-c", "${shell_command} | ${filter_command}"].execute().text
  gcloud_versions_list = "${versions}".tokenize('\n')
} catch (Exception e) {
  return ["Error GCloud", e]
}


def result_list = []
try {
  result_list = s3_versions_list.intersect(gcloud_versions_list)
}catch (Exception e) {
  return ["failed intersect", e]
}

result_list.sort(true) { a,b ->
    a = a.replace("v", "")
    b = b.replace("v", "")
    List verA = a.tokenize('.')
    List verB = b.tokenize('.')

    def commonIndices = Math.min(verA.size(), verB.size())

    for (int i = 0; i < commonIndices; ++i) {
      def numA = verA[i].toInteger()
      def numB = verB[i].toInteger()
      // println "comparing $numA and $numB"

      if (numA != numB) {
        return numA <=> numB
      }
    }

    // If we got this far then all the common indices are identical, so whichever version is longer must be more recent
    verA.size() <=> verB.size()
}.reverse(true)

return result_list
