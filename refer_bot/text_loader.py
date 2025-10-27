def refer_text(link):
	with open('refer_link.txt', 'r') as f:
		return f.read().format(link=link)

def CS_text():
	with open('CS.txt', 'r') as f:
		return f.read()

def intro_text():
	with open('start_intro.txt', 'r') as f:
		return f.read()