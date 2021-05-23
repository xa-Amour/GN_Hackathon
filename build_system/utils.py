# -*- coding: UTF-8 -*-

import os
import re
import sys
import tempfile
import logging

if sys.version_info >= (3,):
    import urllib.request as urllib2
    import urllib.parse as urlparse
else:
    import urllib2
    import urlparse

IS_WINDOWS = (sys.platform == "win32")
IS_MAC = (sys.platform == "darwin")
IS_LINUX = re.search('^linux', sys.platform, re.IGNORECASE)


def get_cmd_output(cmd):
    """Return (status, output) of executing cmd in a shell."""
    if not IS_WINDOWS:
        cmd = '{ ' + cmd + '; }'

    pipe = os.popen(cmd + ' 2>&1', 'r')
    text = ""
    while 1:
        line = pipe.readline()
        if not line:
            break
        text += line
    try:
        sts = pipe.close()
    except:
        sts = -1
    if sts is None:
        sts = 0
    if text[-1:] == '\n':
        text = text[:-1]
    return sts, text


def get_cmd_output_last_line(cmd):
    _, output = get_cmd_output(cmd)
    if len(output) == 0:
        print('No output for: ' + cmd)
        return None

    lines = [s.strip() for s in output.splitlines()]
    if len(lines) < 1:
        print('No output for: ' + cmd)
        return None

    return lines[-1]


def run_cmd(cmd, show_output=True):
    if show_output:
        print(cmd)
    FNULL = open(os.devnull, 'w')
    import subprocess
    if show_output:
        pipe = subprocess.Popen(cmd, stderr=sys.stderr, stdout=sys.stdout, shell=True)
    else:
        pipe = subprocess.Popen(cmd, stderr=FNULL, stdout=FNULL, shell=True)
    ret = pipe.wait()
    FNULL.close()
    return ret


def get_current_repo_name():
    return os.path.basename(get_current_repo_root())


def get_current_branch():
    return get_cmd_output_last_line('git rev-parse --abbrev-ref HEAD')


def get_current_repo_root():
    return get_cmd_output_last_line('git rev-parse --show-toplevel')


def get_branches(re_token):
    _, output = get_cmd_output("git branch -r")
    rep = re.compile(re_token)
    branches = [x.strip() for x in output.splitlines()
                if not not rep.match(x.strip())]
    return branches


def get_merge_base():
    return get_cmd_output_last_line("git show-branch --merge-base")


def puhlish_branch(branch_name=None):
    if not branch_name:
        branch_name = get_current_branch()
    cmd = "git push origin {0}:{1}".format(branch_name, branch_name)
    print(cmd)
    run_cmd(cmd)


def unpublish_branch(branch_name=None):
    if not branch_name:
        branch_name = get_current_branch()
    cmd = "git push origin :{0}".format(branch_name)
    print(cmd)
    run_cmd(cmd)


def get_last_log_of_branch(branch):
    if not branch:
        print('Invalid branch: ' + branch)
        return False

    cmd = 'git log -1 ' + branch

    print(cmd)
    _, output = get_cmd_output(cmd)
    if not output:
        print('No output for ' + cmd)
        return False

    print(output)

    lines = [s.strip() for s in output.splitlines()]
    index_of_log_head = 0
    for v in lines:
        if re.search(r'^commit\s+[a-f\d]{40}$', v):
            break
        index_of_log_head += 1

    return lines[index_of_log_head + 4:]


# Return true if ancestor is ancestor of descendant
def is_ancestor_branch_of(ancestor, descendant):
    status, _ = get_cmd_output(
        'git merge-base --is-ancestor ' + ancestor + ' ' + descendant)
    return 0 == status


def is_descendant_branch_of(ancestor, branch):
    return is_ancestor_branch_of(ancestor, branch)


def valid_jira_name(branch_name):
    valid_jira_re = r'jira/[a-zA-Z]+-\d+'
    p = re.compile(valid_jira_re)
    return p.match(branch_name) is not None


def auto_update_files():
    _, output = get_cmd_output("git status -s")
    lines = output.splitlines()
    for line in lines:
        words = line.split()
        cmd = ""
        if words[0].startswith('A') or words[0].startswith('U'):
            cmd = "git add {}".format(words[1].strip())
        elif words[0].startswith('M'):
            cmd = "git add {}".format(words[1].strip())
        elif words[0].startswith('D'):
            cmd = "git rm --cached {}".format(words[1].strip())
        if len(cmd) != 0:
            run_cmd(cmd)


def get_package_installer():
    if IS_LINUX:
        status = run_cmd("apt -v", False)
        if status == 0:
            return "sudo apt install"
        status = run_cmd("apt-get -v", False)
        if status == 0:
            return "sudo apt-get -y install"
        status = run_cmd("dnf -v", False)
        if status == 0:
            return "sudo dnf install"
        status = run_cmd("yum -v", False)
        if status == 0:
            return "sudo yum install"
        return ""
    elif IS_MAC:
        status = run_cmd("brew -v", False)
        if status == 0:
            return "brew install"
        return ""
    else:
        return ""


def check_tools(tools):
    result = []
    for k in tools.keys():
        cmd = k + " " + tools[k]
        if run_cmd(cmd, False) != 0:
            result.append(k)
    return result


def prepare_tools(tools):
    not_installed_tools = check_tools(tools)
    installer = get_package_installer()
    if len(installer) == 0 and len(not_installed_tools) != 0:
        print("{0} not found, but unable to find installer (apt/apt-get, or yum/dnf, or brew), please install them".format(
            not_installed_tools))
        return

    if len(not_installed_tools) != 0:
        cmd = "{0} {1}".format(installer, " ".join(not_installed_tools))
        status = run_cmd(cmd)
        if status != 0:
            sys.exit(-1)


def download_file(url, dest=None):
    """ 
    Download and save a file specified by url to dest directory,
    """
    u = urllib2.urlopen(url)

    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = os.path.basename(path)
    if not filename:
        filename = 'downloaded.file'
    if dest:
        filename = dest

    with open(filename, 'wb') as f:
        meta = u.info()
        meta_func = meta.getheaders if hasattr(
            meta, 'getheaders') else meta.get_all
        meta_length = meta_func("Content-Length")
        file_size = None
        if meta_length:
            file_size = int(meta_length[0])
        print("Downloading: {0} Bytes: {1}".format(url, file_size))

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)

            status = "{0:16}".format(file_size_dl)
            if file_size:
                status += "   [{0:6.2f}%]".format(
                    file_size_dl * 100 / file_size)
            status += chr(13)
            sys.stdout.write(status)
        sys.stdout.write("\n")
        sys.stdout.flush()

    return filename
