#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gdata.blogger.client
import gdata.client
import gdata.sample_util
import gdata.data
import atom.data
import sys

class Blogger:


	def __init__(self, title=None, body=None, editlink=None):
		self.client = gdata.blogger.client.BloggerClient()
		gdata.sample_util.authorize_client(
			self.client, service='blogger', source='0xPr0xy_blogger_cli',
			scopes=['http://blogger.com/feeds/']
		)
		feed = self.client.get_blogs()
		self.blog_id = feed.entry[0].get_blog_id()

		if title is not None: self.title = title
		else: self.title = False

		if body is not None: self.body = body
		else: self.body = False

		if editlink is not None: self.editlink = editlink
		else: self.editlink = False

		self.execute()


	def printBlogs(self):
		""" print list of users blogs """
		feed = self.client.get_blogs()
		print feed.title.text
		for entry in feed.entry:
			print "\t" + entry.title.text


	def printBlogPosts(self):
		""" print all posts of blog """
		feed = self.client.get_posts(self.blog_id)
		for entry in feed.entry:
			print "\n" + entry.title.text + "\n-------------------------"
			print entry.content.text
			print entry.FindEditLink() + "\n"


	def createPost(self, title, body):
		""" create new post as draft or published """
		return self.client.add_post(self.blog_id, title, body, draft=False)


	def deletePost(self, post_entry):
		""" remove post """
		self.client.delete(post_entry)


	def deleteAllPosts(self):
		""" remove all posts """
		feed = self.client.get_posts(self.blog_id)
		for entry in feed.entry:
			self.deletePost(entry.FindEditLink())


	def execute(self):
		""" determine what method to call """
		if self.title and self.body:
			self.createPost(self.title, self.body)
		elif self.editlink:
			self.deletePost(self.editlink)
		else: self.printBlogPosts()



if len(sys.argv) == 3:
	instance = Blogger(sys.argv[1], sys.argv[2], None)
if len(sys.argv) == 2:
	instance = Blogger(None, None, sys.argv[1])
if len(sys.argv) == 1:
	instance = Blogger()