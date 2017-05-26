#!/usr/bin/env python3
#
# Script to provide a report which should be useful in reviewing Root Cause
# and origin of defects based on work done to fix an issue.
#
# Author: John Eastman <john.eastman@synacor.com>
# Date: May 25, 2017
#
# Changelog
#
# 1.0 - 2017-05-25
# Added:
#  Initial version
#

from datetime import datetime
import argparse
import re
import subprocess
import sys
import textwrap
try:
    from yattag import Doc
except:
    print(textwrap.dedent('''
    Unable to load yattag library needed for report generation.

    To install this library, try:

    pip install yattag
    '''))
    sys.exit(1)
try:
    from jira import JIRA
    from jira.exceptions import JIRAError
except:
    print(textwrap.dedent('''
    Unable to load jira library needed for JIRA information.

    To install this library, try:

    pip install jira
    '''))
    sys.exit(1)


# Constants
# Application Information
PROG = 'bug_review.py'
VERSION = '1.0'
# Connection defaults
JIRA_URL = 'https://jira.corp.synacor.com'
DEFAULT_TIMEOUT = 10


class GitLog:
    'Wrapper for Git Log content'

    def __init__(self, bugId=None):
        if bugId:
            self.bug = bugId
            self.raw_content = GitLog._load_content_for_bug(self.bug)

        if self.raw_content:
            self.content = GitLog._parse_entries(self.raw_content)

    def logBug(bugId):
        return GitLog(bugId=bugId)

    def _load_content_for_bug(bugId):
        cmd = ["git", "log",
               "--no-merges",
               "--oneline",
               "--grep=%s" % bugId]
        logcontent = subprocess.run(cmd,
                                    stdout=subprocess.PIPE)
        return str(logcontent.stdout, 'utf-8').split('\n')

    def _parse_bug_id(message):
        if message:
            match = re.match(r'^.*([a-zA-Z][a-zA-Z][a-zA-Z]+-[0-9]+).*$',
                             message, re.M | re.I)
            if match:
                return match.group(1)
        return None

    def _parse_single_entry(entry):
        result = {}
        result['commit'] = entry[0:10]
        result['message'] = entry[11:]
        result['bug'] = GitLog._parse_bug_id(result['message'])
        return result

    def _parse_entries(loglines):
        result = []
        for line in loglines:
            if line:
                result.append(GitLog._parse_single_entry(line))
        return result

    def getContent(self):
        '''Return parsed content of the log.

        The log entry contains:
        - commit
        - message
        - bug
        '''
        return self.content


class GitMeta:
    'Metadata for a commit'

    def __init__(self, commit):
        self.commit = commit
        self.raw_content = GitMeta._load_content(self.commit)
        self.content = GitMeta._parse_content(self.raw_content)

    def _load_content(commit):
        if commit:
            metacontent = subprocess.run(['git', 'log',
                                          commit + '^!'],
                                         stdout=subprocess.PIPE)
            return str(metacontent.stdout, 'utf-8').split('\n')
        return None

    def _parse_content(content):
        result = {'bug': [], 'notes': []}
        commit_pattern = r'^commit (.*)$'
        date_pattern = r'^Date:\s*(.*)$'
        author_pattern = r'^Author:\s*(.*) (<.*>)$'
        bug_pattern = r'^\s*([a-zA-Z][a-zA-Z][a-zA-Z]+-[0-9]+).*$'
        consume_notes = True
        if content:
            for line in content:
                match = re.match(commit_pattern, line, re.M)
                if match:
                    result['commit'] = match.group(1)
                else:
                    match = re.match(date_pattern, line, re.M)
                    if match:
                        result['date'] = datetime.strptime(
                            match.group(1),
                            '%a %b %d %H:%M:%S %Y %z')
                    else:
                        match = re.match(author_pattern, line, re.M)
                        if match:
                            result['author'] = match.group(1)
                            result['email'] = match.group(2)
                        else:
                            if consume_notes:
                                if line[0:4] == 'diff':
                                    consume_notes = False
                                else:
                                    result['notes'].append(line)
                                    match = re.match(bug_pattern,
                                                     line, re.M | re.I)
                                    if match:
                                        if match.group(1) not in result['bug']:
                                            result['bug'].append(match.group(1))
        return result

    def getContent(self):
        return self.content


class GitDiff:
    'Diff information for a commit without the use of additional tools.'
    lines_pattern = r'^@@ -([0-9]+),[0-9]+ [+]([0-9]+),[0-9]+ @@'
    diff_pattern = r'^diff --git a/([^ ]*) b/(.*)$'
    unparsed_pattern = r'^(---|\+\+\+|[^-+ ])'
    sub_pattern = r'^-'
    add_pattern = r'^[+]'
    file_match = r'^[+][+][+] b/(.*)$'
    line_match = r'^[+]([0-9]*):.*$'
    summary_match = r'^[+]([0-9]*):(.*)$'

    def __init__(self, commit):
        self.commit = commit
        self.prev_commit = commit + '^'
        self.raw_content = GitDiff._load_content(self.commit,
                                                 self.prev_commit)
        self.content = GitDiff._rewrite_diff(self.raw_content)

    def _rewrite_diff(raw_diff):
        left = 0
        right = 0
        lines = []
        files = {}
        current_filename = ''
        current_sectionname = ''
        current_file = []
        current_section = {}
        for line in raw_diff:
            match = re.match(GitDiff.lines_pattern, line, re.M)
            if match:
                current_section = []
                current_sectionname = line
                left = int(match.group(1))
                right = int(match.group(2))
                current_file.append(('@', None, line))
            else:
                match = re.match(GitDiff.unparsed_pattern, line, re.M)
                if match:
                    if line[0:3] == 'dif':
                        if current_section:
                            current_file.append((current_sectionname,
                                                 current_section))
                        if current_file:
                            files[current_filename] = current_file
                        match = re.match(GitDiff.diff_pattern, line, re.M)
                        if match:
                            current_filename = match.group(2)
                            current_file = []
                            current_file.append(('diff', None, line))
                    else:
                        current_file.append((match.group(1), None, line))
                    lines.append((None, None, line))
                else:
                    match = re.match(GitDiff.sub_pattern, line, re.M)
                    if match:
                        current_file.append(('-', left, ' ' + line[1:]))
                        lines.append(('-', left, line[1:]))
                        left += 1
                    else:
                        match = re.match(GitDiff.add_pattern, line, re.M)
                        if match:
                            current_file.append(('+', right, ' ' + line[1:]))
                            lines.append(('+', right, line[1:]))
                            right += 1
                        else:
                            current_file.append(('=', (left, right), line))
                            lines.append(('=', (left, right), line))
                            left += 1
                            right += 1
        if current_section:
            current_file.append((current_sectionname, current_section))
        if current_file:
            files[current_filename] = current_file
        return files

    def _load_content(commit, prev_commit):
        raw_diff = subprocess.run(['git', 'diff',
                                   '-w', '--ignore-all-space',
                                   '--ignore-blank-lines',
                                   commit, prev_commit],
                                  stdout=subprocess.PIPE)
        return str(raw_diff.stdout, 'utf-8').split('\n')

    def _composeLine(line):
        'turn a diff tuple into a line.'
        result = ''
        if line:
            if line[0] is None:
                result = line[2]
            elif line[0] == '-' or line[0] == '+':
                result = '{0}{1}:{2}'.format(line[0],
                                             line[1],
                                             line[2])
            elif line[0] == '=':
                result = '({0},{1}):{2}'.format(line[1][0],
                                                line[1][1],
                                                line[2])
        return result

    def getContent(self):
        return self.content


class GitBlame:
    'Blame information for a commit'
    blame_pattern = r'^([a-f0-9]*)[^\(]*\(([^0-9]+) ([0-9]+-[0-9]+-[0-9]+ [0-9]+:[0-9]+:[0-9]+ [^ ]+)[^0-9]+([0-9]+).*$'

    def __init__(self, commit, diff):
        self.commit = commit
        self.diff = diff
        self.raw_content = GitBlame._load_content(self.commit, self.diff)
        self.content = GitBlame._parse_content(self.raw_content)

    def _load_content(commit, diff):
        files = {}
        if diff:
            for filename in diff:
                lines = list(filter(lambda x: x is not None and
                                    not isinstance(x, tuple),
                                    map(lambda y: y[1],
                                        list(filter(lambda z: z[0] == '+',
                                                    diff[filename])))))

                if lines:
                    cmdline = []
                    cmdline.append("git")
                    cmdline.append("blame")
                    for line in lines:
                        cmdline.append("-L %s,%s" % (line, line))
                    cmdline.append((commit + '^'))
                    cmdline.append("--")
                    cmdline.append(filename)
                    blamecontent = subprocess.run(cmdline,
                                                  stdout=subprocess.PIPE)
                    files[filename] = (str(blamecontent.stdout,
                                           'utf-8').split('\n'))

        return files

    def _parse_content(raw):
        files = {}
        if raw:
            for filename in raw:
                result = {}
                for item in raw[filename]:
                    match = re.match(GitBlame.blame_pattern, item, re.M)
                    if match:
                        result[match.group(4)] = ({'commit': match.group(1),
                                                   'author': match.group(2).rstrip(),
                                                   'date': match.group(3),
                                                   'line': match.group(4)})
                    else:
                        if item:
                            print('!'*30)
                            print('ERROR in MATCH {}'.format(item))
                            print('!'*30)
                files[filename] = result
        return files

    def getContent(self):
        return self.content

    def getSummary(self):
        authors = []
        for c in self.content:
            if c['author'] not in authors:
                authors.append(c['author'])
        return authors


def reportCSS():
    'Returns CSS style for use in report.'
    doc, tag, text = Doc().tagtext()
    with tag('style'):
        text('''html {
          font-family: "Source Sans Pro", sans-serif;
          -ms-text-size-adjust: 100%;
          -webkit-text-size-adjust: 100%;
        }
        body {
          font-family: "Source Sans Pro", sans-serif;
          font-size: 14px;
          line-height: 1.5;
          color: #24292e;
          background-color: #fff;
        }
        td, th {
          padding: 0;
        }
        .float-right {
         float: right !important;
        }
        .commit-info {
          padding: 8px 8px 0;
          margin: 10px 0;
          font-size: 18px;
          background: #eaf5ff;
          border: 1px solid rgba(27,31,35,0.15);
          border-radius: 3px;
        }
        span.title, p.title {
          margin: 0 0 8px;
          font-size: 18px;
          font-weight: 600;
          color: #05264c;
        }
        .commit-info .commit-meta {
          padding: 8px;
          margin-right: -8px;
          margin-left: -8px;
          border-top: 1px solid rgba(27,31,35,0.15);
          border-bottom-right-radius: 3px;
          border-bottom-left-radius: 3px;
        }
        .commit-info .notes pre{
          font-family: "Source Code Pro", monospace;
          font-size: 13px;
          margin: 0px;
        }
        .commit-author-section {
          color: #24292e;
          padding-left: 5px;
        }
        .file {
          position: relative;
          margin-top: 16px;
          margin-bottom: 16px;
          border: 1px solid #ddd;
          border-radius: 3px;
        }
        .file-header {
          padding: 5px 10px;
          background-color: #fafbfc;
          border-bottom: 1px solid #e1e4e8;
          border-top-left-radius: 2px;
          border-top-right-radius: 2px;
        }
        .file-info {
          font-family: "Source Code Pro", monospace;
          font-size: 12px;
          line-height: 32px;
        }
        .file-info span {
          padding-left: 5px;
        }
        .diff-wrapper {
          overflow-x: auto;
          overflow-y: hidden;
          border-bottom-right-radius: 3px;
          border-bottom-left-radius: 3px;
        }
        .diff-table {
          display: table;
          width: 100%;
          border-spacing: 0;
          border-collapse: separate;
          border-color: grey;
        }
        .diff-line-prefix {
          display: inline;
          word-wrap: normal;
          white-space: pre;
          margin: 0;
          padding: 0;
          color: rgba(27,31,35,0.3);
        }
        .transclear {
          color: rgba(0,0,0,0);
        }
        .diff-code {
          position: relative;
          padding-right: 10px;
          padding-left: 10px;
          line-height: 20px;
          vertical-align: top;
        }
        .diff-code-inner {
          overflow: visible;
          font-family: "Source Code Pro", monospace;
          font-size: 12px;
          color: #24292e;
          word-wrap: normal;
          white-space: pre;
        }
        .diff-code-hunk {
          padding-top: 4px;
          padding-bottom: 4px;
          background-color: #f3f8ff;
          border-width: 1px 0;
          color: rgba(27,31,35,0.3);
          vertical-align: middle;
        }
        .diff-line-num {
          height: 20px;
          line-height: 20px;
          font-family: "Source Code Pro", monospace;
          font-size: 12px;
          box-sizing: border-box;
          position: absolute;
          width: 86px;
          padding-left: 2px;
          padding-right: 2px;
          color: rgba(27,31,35,0.3);
          text-align: right;
          border: solid #eeeeee;
          border-width: 0 1px 0 1px;
          vertical-align: top;
          cursor: pointer;
          -webkit-user-select: none;
          -moz-user-select: none;
          -ms-user-select: none;
          user-select: none;
        }
        .diff-line-num .num-left {
          box-sizing: border-box;
          float: left;
          width: 40px;
          overflow: hidden;
          text-overflow: ellipsis;
          padding-left: 3px;
        }
        .diff-line-num .num-right {
          box-sizing: border-box;
          float: right;
          width: 40px;
          overflow: hidden;
          text-overflow: ellipsis;
          padding-left: 3px;
        }
        .diff-commit {
          height: 20px;
          line-height: 20px;
          font-family: "Source Code Pro", monospace;
          font-size: 12px;
          padding-right: 10px;
          padding-left: 76px;
          text-align: right;
          white-space: nowrap;
          vertical-align: top;
          cursor: pointer;
          -webkit-user-select: none;
          -moz-user-select: none;
          -ms-user-select: none;
          user-select: none;
        }
        .diff-author {
          padding-right: 10px;
          padding-left: 10px;
          font-family: "Source Code Pro", monospace;
          font-size: 12px;
          line-height: 20px;
          text-align: right;
          white-space: nowrap;
          vertical-align: top;
          cursor: pointer;
          -webkit-user-select: none;
          -moz-user-select: none;
          -ms-user-select: none;
          user-select: none;
          border-right: 1px solid #eeeeee;
        }
        .commit-1, .commit-2, .commit-3, .commit-4, commit-5, commit-6, commit-7, commit-8 {
        }
        .commit-0 {
          background-color: #eaffea;
        }
        .commit-1 {
          background-color: #fefdb8;
        }
        .commit-2 {
          background-color: #fbefcc;
        }
        .commit-3 {
          background-color: #fff3df;
        }
        .commit-4 {
          background-color: #f4e1d2;
        }
        .commit-5 {
          background-color: #e4d1d1;
        }
        .commit-6 {
          background-color: #f9ccac;
        }
        .commit-7 {
          background-color: #ffef96;
        }
        .commit-8 {
          background-color: #eea29a;
        }
        .details {
          padding: 8px 8px 0;
          margin: 10px 0;
          font-size: 18px;
          background: #eaf5ff;
          border: 1px solid rgba(27,31,35,0.15);
          border-radius: 3px;
          display: block;
        }
        .details .description {
          background-color: #fafbfc;
          padding: 8px;
          margin-right: -8px;
          margin-left: -8px;
          border-top: 1px solid rgba(27,31,35,0.15);
          border-bottom-right-radius: 3px;
          border-bottom-left-radius: 3px;
        }
        .details .description pre {
          font-family: "Source Code Pro", monospace;
          font-size: 13px;
          margin: 0px;
        }
        .property-list-content {
          margin-top: 5px;
          padding-left: 10px;
          display: block;
        }
        .property-list {
          font-family: "Source Code Pro", monospace;
          display: block;
          margin: 0;
          list-style: none;
          padding: 0;
        }
        .property-list:before {
          content: " ";
          display: table;
        }
        .property-list:after {
          clear:both;
          content: " ";
          display: table;
        }
        .property-list .item {
          width: 50%;
          box-sizing: border-box;
          clear: left;
          float: left;
          margin: 1px 0 0 0;
          padding: 0;
          position: relative;
        }
        .property-list .item-right {
          clear: right;
          float: right;
        }
        .property-list .item-wrap {
          padding: 0 10px 0 150px;
          margin: 0;
        }
        .property-list .item-wrap .name {
          text-align: left;
          float: left;
          margin-left: -150px;
          box-sizing: border-box;
          word-wrap: break-word;
          color: #707070;
          display: inline-block;
          font-weight: normal;
          padding: 2px 5px 2px 0;
          padding-right: 5px;
          width: 150px;
        }
        .property-list .item-wrap .value {
          word-wrap: break-word;
          word-break: break-word;
          display: inline-block;
          max-width: 100%;
          padding-bottom: 2px;
          padding-left: 5px;
          padding-top: 2px;
          position: relative;
          vertical-align: top;
        }
        footer {
          text-align: center;
          width: auto;
          margin-right: 10px;
          color: rgba(27,31,35,0.3);
          padding; 9px 0 9px 0;
          font-size: 50%;
        }''')
    return doc.getvalue()


def reportFooter():
    'Generate the footer portion of report.'
    doc, tag, text = Doc().tagtext()
    with tag('footer'):
        text('Generated with {} version {} on {}'.format(PROG,
                                                         VERSION,
                                                         datetime.now()
                                                         .isoformat()))
    return doc.getvalue()


def reportJiraField(label, field, left):
    'Generate content for JIRA field for report.'
    doc, tag, text, line = Doc().ttl()
    position = ''
    if not left:
        position = ' item-right'
    with tag('li', klass='item' + position):
        with tag('div', klass='item-wrap'):
            with tag('strong', klass='name'):
                text(label)
            with tag('span', klass='value'):
                if field == 'Bug':
                    line('i', 'bug_report',
                         klass='material-icons md-18',
                         style='vertical-align: middle')
                elif field == 'Fixed':
                    line('i', 'done',
                         klass='material-icons md-18',
                         style='vertical-align: middle')
                elif label == 'Labels' and field:
                    line('i', 'local_offer',
                         klass='material-icons md-18',
                         style='vertical-align: middle')
                text(field)
    return doc.getvalue()


def reportHeader(bugId, issue):
    'Generate header section of the report.'
    doc, tag, text = Doc().tagtext()
    with tag('div', klass='details'):  # bug information
        with tag('div'):  # bug header
            with tag('div'):  # bug ID
                with tag('p', klass='title'):
                    text(bugId)
            with tag('div'):  # bug title
                with tag('p', klass='title'):
                    text(issue.fields.summary)
        with tag('div', klass='property-list-content'):  # bug metadata
            with tag('ul', klass='property-list'):
                components = ''
                resolution = ''
                doc.asis(reportJiraField('Type',
                                         issue.fields.issuetype.name,
                                         True))

                doc.asis(reportJiraField('Status',
                                         issue.fields.status.name,
                                         False))

                doc.asis(reportJiraField('Affects Version/s',
                                         ', '.join([x.name for x in issue.fields.versions]),
                                         True))

                if issue.fields.resolution:
                    resolution = issue.fields.resolution.name
                doc.asis(reportJiraField('Resolution',
                                         resolution,
                                         False))

                doc.asis(reportJiraField('Fix Version/s',
                                         ', '.join([x.name for x in issue.fields.fixVersions])
                                         , True))

                if issue.fields.components:
                    components = ', '.join([x.name for x in issue.fields.components])
                doc.asis(reportJiraField('Component/s',
                                         components,
                                         False))

                doc.asis(reportJiraField('Severity',
                                         issue.fields.customfield_10020.value,
                                         True))

                doc.asis(reportJiraField('Labels',
                                         ', '.join(issue.fields.labels),
                                         False))
        with tag('div', klass='description'):  # bug description
            with tag('pre'):
                text(issue.fields.description)

    return doc.getvalue()


def htmlReport(bugId, head, content):
    'Generate an HTML report.'
    doc, tag, text = Doc().tagtext()
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('head'):
            doc.stag('meta', charset='utf-8')
            with tag('title'):
                text(bugId)
            doc.stag('link',
                     href='https://fonts.googleapis.com/icon?family=Material+Icons|Source+Code+Pro|Sorce+Sans+Pro',
                     rel='stylesheet')
            doc.asis(reportCSS())
        with tag('body'):
            doc.asis(head)
            if isinstance(content, list):
                for line in content:
                    doc.asis(line)
            else:
                doc.asis(content)
        doc.asis(reportFooter())
    return doc.getvalue()


def reportCommitMeta(commit, author, klass):
    'Generate metadata section of report for a commit.'
    doc, tag, text, line = Doc().ttl()
    with tag('div', klass='commit-meta ' + klass):
        line('i', 'face', klass='material-icons md-18',
             style='vertical-align: middle')
        with tag('span', klass='commit-author-section'):
            text(author)
        with tag('span', klass='float-right'):
            text('commit ' + commit)
    return doc.getvalue()


def reportReplacedMeta(commit, author, date, notes, klass):
    'Generate replaced commit section for a commit of report.'
    doc, tag, text = Doc().tagtext()
    with tag('div', klass='commit-meta ' + klass):
        doc.asis(reportCommitText(notes, date, klass=klass))
        doc.asis(reportCommitMeta(commit,
                                  author,
                                  klass))
    return doc.getvalue()


def reportCommitText(notes, date, klass=''):
    'Generate commit text portion of report.'
    doc, tag, text = Doc().tagtext()
    klass_text = 'title'
    if klass:
        klass_text = klass_text + ' ' + klass
    with tag('div', klass=klass):
        with tag('span', klass='title'):
            if len(notes) > 2:
                text(notes[1])
        with tag('span', klass='float-right'):
            text(date.isoformat())
    with tag('div', klass='notes ' + klass):
        with tag('pre'):
            if len(notes) > 2:
                for note in notes[2:]:
                    text(note + '\n')
    return doc.getvalue()


def reportCommitHeader(commit, replaced, meta, commitmap):
    'Generate commit header section of report.'
    doc, tag, text = Doc().tagtext()
    with tag('div', klass='commit-info'):
        doc.asis(reportCommitText(meta[commit]['notes'],
                                  meta[commit]['date'], ''))
        doc.asis(reportCommitMeta(meta[commit]['commit'],
                                  meta[commit]['author'],
                                  commitmap[commit]))
        with tag('div'):
            with tag('p', style='text-align:center'):
                text('Replaces content from the following commits')
        for r in replaced:
            doc.asis(reportReplacedMeta(meta[r]['commit'],
                                        meta[r]['author'],
                                        meta[r]['date'],
                                        meta[r]['notes'],
                                        commitmap[r]))

    return doc.getvalue()


def reportCommitFile(filename, diffcontent):
    'Generate file section of report.'
    doc, tag, text = Doc().tagtext()
    with tag('div'):
        with tag('div'):
            text(filename)
        with tag('div'):
            doc.asis(diffcontent)
    return doc.getvalue()


def reportDiffLine(codeline):
    'Generte a diff line of report.'
    doc, tag, text = Doc().tagtext()
    with tag('tr'):
        with tag('td', klass='diff-code diff-code-inner diff-code-hunk'):
            pass
        with tag('td', colspan='3',
                 klass='diff-code diff-code-inner diff-code-hunk'):
            text(codeline[2])
    return doc.getvalue()


def reportDiffSameLine(codeline):
    'Generate a diff line where content is the same of report.'
    doc, tag, text, line = Doc().ttl()
    with tag('tr'):
        with tag('td', klass='diff-line-num'):
            with tag('div', klass='num-left'):
                text(codeline[1][0])
            with tag('div', klass='num-right'):
                text(codeline[1][1])
        with tag('td', klass='diff-commit'):
            pass
        with tag('td', klass='diff-author'):
            pass
        with tag('td', klass='diff-code'):
            with tag('span', klass='diff-line-prefix transclear'):
                line('i', 'check_box_outline_blank',
                     klass='material-icons',
                     style='vertical-align: middle; font-size:14px;')
            with tag('span', klass='diff-code-inner'):
                text(codeline[2])
    return doc.getvalue()


def reportDiffPlusLine(codeline, blame, commit_map):
    'Generate a diff line for a + commit of report.'
    doc, tag, text, line = Doc().ttl()
    commit = blame.get(str(codeline[1]), {})\
                  .get('commit', 'ERR')
    author = blame.get(str(codeline[1]), {})\
                  .get('author', 'ERR')
    with tag('tr'):
        with tag('td', klass='diff-line-num'):
            with tag('div', klass='num-left'):
                pass
            with tag('div', klass='num-right'):
                text(codeline[1])
        with tag('td', klass='diff-commit ' + commit_map.get(commit, '')):
            text(commit)
        with tag('td', klass='diff-author ' + commit_map.get(commit, '')):
            text(author)
        with tag('td', klass='diff-code ' + commit_map.get(commit, '')):
            with tag('span', klass='diff-line-prefix'):
                line('i', 'block',
                     klass='material-icons',
                     style='vertical-align: middle; font-size:14px;')
                #  text('-')  # reversed because of diff comparison
            with tag('span', klass='diff-code-inner'):
                text(codeline[2])
    return doc.getvalue()


def reportDiffMinusLine(codeline, commit, author, commit_map):
    'Generate a diff line or a - commit of report.'
    doc, tag, text, line = Doc().ttl()
    with tag('tr'):
        with tag('td', klass='diff-line-num'):
            with tag('div', klass='num-left'):
                text(codeline[1])
            with tag('div', klass='num-right'):
                pass
        with tag('td', klass='diff-commit ' + commit_map[commit]):
            text(commit)
        with tag('td', klass='diff-author ' + commit_map[commit]):
            text(author)
        with tag('td', klass='diff-code ' + commit_map[commit]):
            with tag('span', klass='diff-line-prefix'):
                line('i', 'add',
                     klass='material-icons',
                     style='vertical-align: middle; font-size:14px;')
                # text('+')  # reversed because of diff comparison
            with tag('span', klass='diff-code-inner'):
                text(codeline[2])
    return doc.getvalue()


def reportDiff(diff, blame, author, commit, commitmap):
    'Generate the diff section of report.'
    doc, tag, text, line = Doc().ttl()
    for filename in diff:
        with tag('div', klass='file'):
            with tag('div', klass='file-header'):
                with tag('div', klass='file-info'):
                    line('i', 'insert_drive_file',
                         klass='material-icons',
                         style='vertical-align: middle; font-size:12px')
                    with tag('span'):
                        text(filename)
            with tag('div', klass='diff-wrapper'):
                with tag('table', klass='diff-table'):
                    with tag('tbody'):
                        fileitem = diff[filename]
                        fileblame = blame.get(filename, {})
                        for item in fileitem:
                            if item[0] == 'diff' or item[0] == 'i' or \
                               item[0] == '---' or item[0] == '+++' or \
                               item[0] == 'd':
                                pass  # skip these entries
                            elif item[0] == '@':
                                doc.asis(reportDiffLine(item))
                            elif item[0] == '=':
                                doc.asis(reportDiffSameLine(item))
                            elif item[0] == '+':
                                doc.asis(reportDiffPlusLine(item,
                                                            fileblame,
                                                            commitmap))
                            elif item[0] == '-':
                                doc.asis(reportDiffMinusLine(item,
                                                             commit,
                                                             author,
                                                             commitmap))
                            else:
                                print('MISSED: {}'.format(item))
    return doc.getvalue()


def extendCommitSet(commit, blame, commits, committree):
    '''Add to the set of commits associated with the report.

    Generates an updated set of commits as well as the child commits for
    the specified commit.
    '''
    localcommits = commits.copy()
    localtree = committree.copy()
    branch = set()
    localcommits.add(commit)
    for filename in blame:
        for line in blame[filename]:
            found_commit = blame[filename][line]['commit']
            if found_commit not in localcommits:
                localcommits.add(found_commit)
            branch.add(found_commit)
    localtree[commit] = branch
    return((localcommits, localtree))


def extendCommitMap(commit, commits, commitmap, index=0):
    '''Add to the mapping of commits to css class names.

    This helps to provide consistent styling of commits across sections of
    the report.
    '''
    mapping = ['commit-1',
               'commit-2',
               'commit-3',
               'commit-4',
               'commit-5',
               'commit-6',
               'commit-7',
               'commit-8']
    count = index
    localmap = commitmap.copy()
    # override mapping for major commits
    localmap[commit] = 'commit-0'
    for c in commits:
        if c not in localmap:
            localmap[c] = mapping[count]
            count += 1
        if count >= len(mapping):
            count = 0
    return((localmap, count))


def createReport(bugId, jira, outfile):
    'Create the report.'
    issue = jira.issue(bugId)
    reportcontent = []
    commitcontent = []
    maincommits = set()  # commits to use for header overview
    commits = set()  # set of all commits
    committree = {}  # main commits with commits replaced
    commitmap = {}
    commitmeta = {}
    mapindex = 0
    log = GitLog.logBug(bugId)
    logcontent = log.getContent()
    for entry in logcontent:
        commit = entry['commit']
        maincommits.add(commit)
        commitmeta[commit] = GitMeta(commit).getContent()
        diff = GitDiff(commit)
        blame = GitBlame(commit, diff.getContent())
        commits, committree = extendCommitSet(commit,
                                              blame.content,
                                              commits,
                                              committree)
        commitmap, mapindex = extendCommitMap(commit,
                                              commits,
                                              commitmap,
                                              mapindex)
        #  build meta info for replaced commits
        for replaced in committree[commit]:
            if replaced not in commitmeta:
                commitmeta[replaced] = GitMeta(replaced).getContent()
        commitcontent.append(reportCommitHeader(commit,
                                                committree[commit],
                                                commitmeta,
                                                commitmap))
        commitcontent.append(reportDiff(diff.content,
                                        blame.content,
                                        commitmeta[commit]['author'],
                                        commit,
                                        commitmap))
    reportcontent.extend(commitcontent)
    report = htmlReport(bugId,
                        reportHeader(bugId, issue),
                        reportcontent)
    outfile.write(report)


def connectToJira(url, timeout):
    'Attempt a connection to JIRA. Returns None on failure.'
    jira_options = {
        'server': JIRA_URL
    }

    try:
        jira = JIRA(jira_options, validate=True, timeout=timeout)
    except JIRAError as e:
        if e.status_code == 401:
            sys.stderr.write(textwrap.dedent('''
            Failed to authenticate to JIRA.

            JIRA responded with:
            {}

            Please check that you have added your credentials to your
            ~/.netrc file.
            ''').format(e.text))
        else:
            sys.stderr.write(textwrap.dedent('''
            Failed to connect to JIRA.

            {}
            ''').format(e.text))
        jira = None
    return jira


if __name__ == "__main__":
    description = textwrap.dedent('''
    Generate bug report useful for reviewing Root Cause and origin of
    defects based on work donr to fix an issue.

    Report is generated as an HTML file either to standard out or to a file
    as specified with program arguments.

    This utilitiy is expected to be run from within the git directory of the
    associated project at the top level.

    Credentials for JIRA are loaded from inside the ~/.netrc file. Please
    make sure your credentials are entered in this file.

    This utility depends on several external tools which you should ensure are
    installed on your system:
    - git - the common git tool
    ''')

    parser = argparse.ArgumentParser(
        prog=PROG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description)
    parser.add_argument('bug', action='store',
                        help='''JIRA ID for issue''')
    parser.add_argument('-o', '--output',
                        nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='Name of output file')
    parser.add_argument('--timeout', type=int, action='store',
                        dest='timeout',
                        default=DEFAULT_TIMEOUT,
                        help='JIRA connection timeout in seconds.')
    parser.add_argument('--jira', action='store',
                        dest='url',
                        default=JIRA_URL,
                        help='URL of JIRA server')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + VERSION)
    args = parser.parse_args()

    jira = connectToJira(JIRA_URL, args.timeout)
    if not jira:
        sys.exit(1)

    createReport(args.bug, jira, args.output)
