#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Blogger
import gdata.blogger.client
import gdata.client
import gdata.sample_util
import gdata.data
import atom.data
import sys

#ItemWidget
import urwid

#Picasa
import gdata.photos.service
import gdata.media
import gdata.geo
import getpass 



class Picasa:

	def upload(self,filename, title):
		
		gd_client = gdata.photos.service.PhotosService()
		gd_client.email  = raw_input('Please enter your picasa username:\n')
		gd_client.password = getpass.getpass('Password:\n')
		gd_client.source = '0xPr0xy_picasa_cli'
		gd_client.ProgrammaticLogin()
		album_url = '/data/feed/api/user/%s/albumid/default/' % gd_client.email
		photo = gd_client.InsertPhotoSimple(album_url, title,'Uploaded using the very lame picasa API :p', filename, content_type='image/jpeg')
		print '\nUpload finished...\nPosting to blogger...\n'
		return photo.GetMediaURL()


class ItemWidget (urwid.WidgetWrap):

    def __init__ (self, entry, detail=None):
        
        #list view
        if entry is not None and detail is None:
        	self.open = entry #limit content? [:25]
        	self.remove = entry.FindEditLink()
        	self.item = [
        		urwid.Padding(urwid.AttrWrap(
        		urwid.Text('%s' % entry.title.text),  'body', 'focus'),  left=2),
        	]
        #detail view
        elif entry is not None and detail is not None:
        	self.item = [
        		urwid.Padding(urwid.AttrWrap(
        		urwid.Text('%s' % entry),  'body', 'focus'),  left=2),
        	]

        w = urwid.Columns(self.item)
        self.__super.__init__(w)

    def selectable (self):
        return True

    def keypress(self, size, key):
        return key



class Blogger:


	def __init__(self, title=None, body=None, editlink=None, filename=None):

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

		if filename is not None: self.filename = filename
		else: self.filename = False
		
		self.count = 1
		self.execute()


	def openBlogPost(self, entry):
		"""open blog post view content"""
		self.detail = []
		self.detail.append(ItemWidget(entry.title.text, 'detail'))
		self.detail.append(ItemWidget(entry.content.text, 'detail'))
		self.listbox = urwid.ListBox(urwid.SimpleListWalker(self.detail))
		self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'))
		self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.returnToList)
		self.loop.run()

	def printBlogPosts(self):
		""" open all posts of blog in urwid interface """
		
		feed = self.client.get_posts(self.blog_id)
		self.palette = [
			('body','dark cyan', '', 'standout'),
			('focus','dark red', '', 'standout'),
			('head','light red', 'black'),
		]	
		self.blogitems = []
		for entry in feed.entry:

			self.blogitems.append(ItemWidget(entry))
			self.count += 1
		
		self.listbox = urwid.ListBox(urwid.SimpleListWalker(self.blogitems))
		self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'))
		self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke)
		self.loop.run()


	def createPost(self, title, body):
		""" create new post as draft or published """
		return self.client.add_post(self.blog_id, title, body, draft=False)


	def createPostWithImage(self,title, body, filename):
		""" create new post with image uploaded to picasa dropbox """
		pic = Picasa()
		imageurl = pic.upload(filename, title)
		body += '<p><img src=\'' + imageurl + '\'/></p>'
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
		if self.title and self.body and self.filename:
			self.createPostWithImage(self.title, self.body, self.filename)
		elif self.title and self.body:
			self.createPost(self.title, self.body)
		elif self.editlink:
			self.deletePost(self.editlink)
		else: self.printBlogPosts()


	def returnToList (self,input):
		""" handle keystrokes """
		
		if input in ('q', 'Q'):
			self.printBlogPosts()

	def keystroke (self,input):
		""" handle keystrokes """
		
		if input in ('q', 'Q'):
			raise urwid.ExitMainLoop()
		
		if input is 'enter':
			try:
				self.focus = self.listbox.get_focus()[0].open
			except Exception as e:
				pass
			#self.view.set_header(urwid.AttrWrap(urwid.Text(
			#	'selected: %s' % str(self.focus)), 'head'))
			self.openBlogPost(self.focus)

		if input is 'backspace':	
			try:
				self.focus = str(self.listbox.get_focus()[0].remove)
			except Exception as e:
				pass
			try: 
				self.focus.index('blogger')
				self.deletePost(self.focus)
				sys.exit('deleted: %s' % self.focus)
			except ValueError:
				self.view.set_header(urwid.AttrWrap(urwid.Text(
				'NO DELETE LINK!'), 'head'))


if len(sys.argv) == 4:
	instance = Blogger(sys.argv[1], sys.argv[2], None, sys.argv[3])
if len(sys.argv) == 3:
	instance = Blogger(sys.argv[1], sys.argv[2], None)
if len(sys.argv) == 2:
	instance = Blogger(None, None, sys.argv[1])
if len(sys.argv) == 1:
	instance = Blogger()