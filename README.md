An interesting area of online learning is a classification setting where the true label is not
known and the algorithm must learn from partial feedback that is available. The Banditron
applies ideas from the full information setting to the bandit model and balances exploration
and exploitation. We plan to extend the Banditron algorithm which learns multi-class
classification in an online supervised learning setting with partial feedback. The problem of
particular interest to us is to predict r labels (using label rankings based on our model) and
explore with a probability γ by replacing one (or maybe more) labels with a random label
ranked lower by our model. This can be applied to a lot of real world applications such as
recommendation systems where a user is recommended r relevant items with some random
items included.


####################
Requirements
####################

1. Mongo (To avoid I/O reads from local file system, we are using MongoDB to store data)

2. PyMongo
