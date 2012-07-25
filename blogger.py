#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gdata.blogger.client
import gdata.client
import gdata.sample_util
import gdata.data
import atom.data
import sys
import gdata.photos.service
import gdata.media
import gdata.geo
import urwid


class ItemWidget (urwid.WidgetWrap):

    def __init__ (self, description=None, id=None):
        
        if id is not None and description is not None:

        	self.content = 'Post %s: %s...' % (str(id), description)
        	self.item = [
            	('fixed', 15, urwid.Padding(urwid.AttrWrap(
            	urwid.Text('Post %s' % str(id)), 'body', 'focus'), left=2)),
            	urwid.AttrWrap(urwid.Text('%s' % description), 'body', 'focus'),

        	]
        
        elif description is not None:

        	self.content = '%s' % description #limit content? [:25]
        	self.item = [
        		urwid.Padding(urwid.AttrWrap(
        		urwid.Text('%s' % description),  'body', 'focus'),  left=15),
        	]

        else:

        	self.item = [
        		urwid.Padding(urwid.AttrWrap(
        		urwid.Divider(u'-'),  'body', 'head'),  left=15),
        	]
        
        w = urwid.Columns(self.item)
        self.__super.__init__(w)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key


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
		
		self.count = 1
		
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
		
		self.palette = [
			('body','dark cyan', '', 'standout'),
			('focus','dark red', '', 'standout'),
			('head','light red', 'black'),
		]	


		self.blogitems = []
		

		for entry in feed.entry:

			self.blogitems.append(ItemWidget(entry.title.text, self.count))
			self.blogitems.append(ItemWidget(entry.content.text, None))
			self.blogitems.append(ItemWidget(entry.FindEditLink(), None))
			self.blogitems.append(ItemWidget(None,None))
			self.count += 1
		
		self.header = urwid.AttrMap(urwid.Text('selected:'), 'head')
		self.listbox = urwid.ListBox(urwid.SimpleListWalker(self.blogitems))
		self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'), header=self.header)
		self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke)
		self.loop.run()

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


	def keystroke (self,input):

		
		if input in ('q', 'Q'):
			raise urwid.ExitMainLoop()

		if input is 'enter':
			
			try:
				self.focus = self.listbox.get_focus()[0].content
			except Exception as e:
				pass

			self.view.set_header(urwid.AttrWrap(urwid.Text(
				'selected: %s' % str(self.focus)), 'head'))

		if input is 'backspace':
			
			try:
				self.focus = str(self.listbox.get_focus()[0].content)
			except Exception as e:
				pass

			try: 
				self.focus.index('blogger')
				self.deletePost(self.focus)
				sys.exit('deleted: %s' % self.focus)
			except ValueError:
				self.view.set_header(urwid.AttrWrap(urwid.Text(
				'NO DELETE LINK!'), 'head'))


if len(sys.argv) == 3:
	instance = Blogger(sys.argv[1], sys.argv[2], None)
if len(sys.argv) == 2:
	instance = Blogger(None, None, sys.argv[1])
if len(sys.argv) == 1:
	instance = Blogger()