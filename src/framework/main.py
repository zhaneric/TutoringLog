#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
from google.appengine.api import users
from google.appengine.ext import db

def is_debug():
    return os.path.isfile('static/debug') 

def html_print(request, filename, *parts):
    with open('static/html/' + filename + '.html', 'r') as content_file:
        request.response.out.write(content_file.read() % parts)
        request.response.out.write("\n")

def script_print(request, filename):
    if filename.startswith('http'):
        request.response.out.write("<script src=\"" + filename + "\"></script>\n")
    else:
        request.response.out.write("<script src=\"static/js/" + filename + ".js\"></script>\n")

def html_start(request):
    request.response.out.write("<!DOCTYPE html>\n<html>\n")

def head_start(request):
    request.response.out.write("<head>\n")

def title_set(request, title):
    request.response.out.write("<title>" + title + "</title>\n")

def head(request):
    html_print(request, 'head')

def head_end(request):
    request.response.out.write("</head>\n")

def body_start(request):
    request.response.out.write("<body>\n")

def body_end(request):
    request.response.out.write("</body>\n")

def html_end(request):
    request.response.out.write("</html>")


def style_print(request, filename):
    if filename.startswith('http'):
        request.response.out.write("<link rel=\"stylesheet\" href=\"" + filename + "\">\n")
    else:
        request.response.out.write("<link rel=\"stylesheet\" href=\"static/css/" + filename + ".css\">\n")

def logout_html():
    return '<div id = "user">Logged in as <span id = "user-email">' + users.get_current_user().email() + '</span> | <a id ="logout-link" href = "' + users.create_logout_url("/") + '">sign out</a></div>'


def page(link, text):
    return '<div><a href = "' + link + '" id = "page-' + link + '">' + text + '</a></div>'


def other_pages_html(student, member, admin):
    val = ''
    if student: val += page('student', 'I was tutored by another member')
    if member:  val += page('member', 'View my tutoring log')
    if admin:   val += page('admin', 'Open administrator page')
    return val

def club_member():
    q = db.GqlQuery("SELECT * FROM Tutor WHERE email = '" + users.get_current_user().email() + "'")
    return q.get()

def restricted_domain():
    return "@hcrhs.org"

def is_valid_user():
    return users.get_current_user().email().endswith(restricted_domain()) or restricted_domain() == '' or users.is_current_user_admin()