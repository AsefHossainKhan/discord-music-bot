class yt:
  def __init__(self, title, url): 
    self.title = title 
    self.url = url

test = []
test.append(yt('Youtube 1', 'http://www.youtube.com'))
test.append(yt('Youtube 2', 'http://www.youtube2.com'))

for index, item in enumerate(test):
  print(f"{index+1}. {item.title}")