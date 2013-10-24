
import LSI

titles = [ 
	"The Neatest Little Guide to Stock Market Investing", 
	"Investing For Dummies, 4th Edition", 
	"The Little Book of Common Sense Investing: The Only Way to Guarantee Your Fair Share of Stock Market Returns", 
	"The Little Book of Value Investing", 
	"Value Investing: From Graham to Buffett and Beyond", 
	"Rich Dad's Guide to Investing: What the Rich Invest in, That the Poor and the Middle Class Do Not!", 
	"Investing in Real Estate, 5th Edition", 
	"Stock Investing For Dummies", 
	"Rich Dad's Advisors: The ABC's of Real Estate Investing: The Secrets of Finding Hidden Profits Most Investors Miss" 
	]
stopwords = set(['and','edition','for','in','little','of','the','to','this','that','a','an'])
ignorechars = ''',:'!'''
mylsa = LSI.LSI(stopwords, ignorechars) 
for t in titles:
	mylsa.parse(t)
	mylsa.build() 
	mylsa.printA()