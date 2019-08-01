class Recipe:
    
    def __init__(self, source, url, title, numWordsBeforeRecipe, author, estimatedTime, uniquePath):
        self.source = source
        self.url = url
        self.title = title
        self.numWordsBeforeRecipe = numWordsBeforeRecipe
        self.author = author
        self.estimatedTime = estimatedTime
        self.uniquePath = uniquePath
        
    def returnTuple(self):
        return (self.source, self.uniquePath, self.title, self.numWordsBeforeRecipe, self.url, self.estimatedTime, self.author)