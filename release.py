#!/usr/bin/env python

import collections
import httplib
import json
import os
import sys
import subprocess

this_dir = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(this_dir, "dist")
setup_py = os.path.join(this_dir, "setup.py")

def ordered_hook(pairs):
    ordered = collections.OrderedDict()
    for pair in pairs:
        ordered[pair[0]] = pair[1]
    return ordered

class ReleaseCommand(object):
    def __init__(self):
        self.package = json.load(open("setup.json", "r"),
                object_pairs_hook = ordered_hook)

        self.tarball_name = "%s-%s.tar.gz" % \
            (self.package["name"], self.package["version"])

        self.tarball = os.path.join(dist_dir, self.tarball_name)

    def run(self, *args):
        print "-> %s" % " ".join(args)
        return subprocess.check_output(args)

    def read_access_token(self):
        access_token = self.run("git", "config", "github.files.accesstoken")
        self.access_token = access_token.strip()

    def github_api(self, path, data):
        body = json.dumps(data)
        path += "?access_token=%s" % self.access_token

        connection = httplib.HTTPSConnection("api.github.com")
        connection.request("POST", path, body = body)
        response = connection.getresponse()
        response_body = response.read()
        connection.close()

        data = json.loads(response_body)
        if "errors" in data:
            print >>sys.stderr, "Github Response Failed: %s" % data["message"]
            for error in data["errors"]:
                print >>sys.stderr, "    Error: %s\n" % error["code"]
        return data

    def github_upload(self):
        self.read_access_token()
        description = "%s version %s" % \
            (self.package["name"], self.package["version"])

        data = self.github_api("/repos/marshall/logcat-color/downloads", {
            "name": self.tarball_name,
            "size": os.stat(self.tarball).st_size,
            "description": description,
        })

        print data

        self.run("curl",
            "-F", "key=%s" % data["path"],
            "-F", "acl=%s" % data["acl"],
            "-F", "success_action_status=201",
            "-F", "Filename=%s" % data["name"],
            "-F", "AWSAccessKeyId=%s" % data["accesskeyid"],
            "-F", "Policy=%s" % data["policy"],
            "-F", "Signature=%s" % data["signature"],
            "-F", "Content-Type=%s" % data["mime_type"],
            "-F", "file=@%s" % self.tarball,
            data["s3_url"])

    def help(self):
        print """
Usage: %s <command> [args]
Supported commands:
    help            view this help message
    build           build source distribution and create a git tag
    tag             create the git tag for the version in setup.py
    push            push the release tarball to github and pypi, and push git tags
    bump [version]  bump to [version] in setup.json, stage, and prepare a commit message
""" % sys.argv[0]

    def build(self):
        # build sdist
        self.run(sys.executable, setup_py, "sdist")

        print "%s succesfully built. to tag, use %s tag\n" % \
            (self.tarball_name, sys.argv[0])

    def tag(self):
        self.run("git", "tag", "v%s" % self.package["version"])

        print "git tag \"v%s\" created. to push the release, use %s push\n" % \
            (self.package["version"], sys.argv[0])

    def push(self):
        # upload source tarball->github, and setup.py upload for pypi
        self.github_upload()
        self.run(sys.executable, setup_py, "sdist", "upload")
        self.run("git", "push", "--tags")

        print "%s successfully uploaded, and v%s tag pushed. to bump, use %s bump\n" % \
            (self.tarball_name, self.package["version"], sys.argv[0])

    def bump(self):
        if len(sys.argv) < 3:
            print >>sys.stderr, "Error: bump requires a version to bump to"
            sys.exit(1)

        bump_version = sys.argv[2]
        self.package["version"] = bump_version

        setup_json = json.dumps(self.package,
            separators = (',', ': '),
            indent = 4)

        open("setup.json", "w").write(setup_json)
        message = "bump to version %s" % bump_version

        os.execv("/usr/bin/git", ("commit", "-v", "-m", message, "-e"))

    def main(self):
        command = "help"
        if len(sys.argv) > 1:
            command = sys.argv[1]

        if command == "help":
            self.help()
        elif command == "build":
            self.build()
        elif command == "tag":
            self.tag()
        elif command == "push":
            self.push()
        elif command == "bump":
            self.bump()


if __name__ == "__main__":
  ReleaseCommand().main()
