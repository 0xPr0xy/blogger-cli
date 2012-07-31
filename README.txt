This is a blogger client for the command line


Requirements:
--------------
Google Account


Commands:
---------
view posts 			./blogger
create post 			./blogger '<title>' "<body>"
create post with image		./blogger '<title>' "<body>" '<image>'


Controls:
---------
up = scroll up
down = scroll down
enter = post details
backspace = remove post (and from detail view does nothing)
q = quit (and from detail view returns to list)


Example usage:
---------------
./blogger.py 'Hello World!' "First post from command line through Google's Blogger API ^^"

./blogger.py 'Wow, lets try a link!' "A post with link <a href='http://0xpr0xy.blogspot.nl/'>http://0xpr0xy.blogspot.nl/</a>"

./blogger.py 'Wow, lets try an image!' "A post with image" 'image.png'




Enjoy!

0xPr0xy