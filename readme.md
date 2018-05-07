# What causes Yelp businesses to close?
## Business Understanding
Can help restaurants know what to focus on to protect their downside.
## Data Understanding
The Yelp Academic dataset provides a snapshot of data on Yelp businesses from January 2018. The businesses have been run through the Google Maps API to find out if they have closed (as of May 6, 2018).
## Data Preparation
Additionally, I will be cleaning columns, some of which include: categories, hours open, is it part of a chain, and city. I would also like to integrate some third party data if possible, particularly: average rent price in that city/location and unemployment rate. This article provides additional suggestions:
https://towardsdatascience.com/using-yelp-data-to-predict-restaurant-closure-8aafa4f72ad6
## Modeling
I will use a Random Forest model that will output a closure probability for each business and then a classifier that will test the success of my model
## Evaluation
I will run a train test split on the Yelp Academic Dataset. I also may want to run the model on businesses that are currently open and see if they close.
## Deployment
This will provide an online report of the factors most associated with a Yelp business closing, and the ability to get a closing probability for any currently open business.
