@Grab(group='org.jsoup', module='jsoup', version='1.7.3')
import org.jsoup.Jsoup;
import org.boon.Boon;

def doc = Jsoup.connect('http://example.com/dir/list/').get()
def versions = []
doc.select("pre > a").each{href ->
  def filename = href.text()
  if(filename.endsWith("/") && filename != "../") {
    versions.add('"' + filename.substring(0, filename.length()-1) + '"')
  }
}

versions.sort(true) { a,b ->
    a = a.replace("\"", "")
    b = b.replace("\"", "")
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

def form_properties = /
  disable_edit_json: true,
  disable_properties: true,
  no_additional_properties: true,
  disable_collapse: false,
  disable_array_add: false,
  disable_array_delete: false,
  disable_array_reorder: false,
  theme: "bootstrap2",
  iconlib:"fontawesome3"
/;

def form_body = /
  "title": "Deploy",
  "type": "object",
  "properties": {
    "versions": {
      "type": "array",
      "format": "table",
      "title": "Versions",
      "uniqueItems": true,
      "items": {
        "type": "object",
        "title": "version",
        "properties": {
          "version": {
            "type": "string",
            "enum": [ / + versions.join(", ") + / ],
            "default": / + versions[0] + /

          },
          "percent": {
            "type": "integer",
            "default": 100
          }
        }
      },
      "default": [
        {
          "version": / + versions[0] + /,
          "percent": 100
        }
      ]
    }
  }
/;

def jsonEditorOptions = Boon.fromJson('{ ' + form_properties + ', "schema": {' + form_body + '} }');
return jsonEditorOptions;
