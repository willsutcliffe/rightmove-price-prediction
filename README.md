
# London property price prediction

## Motivation

I did this project as I spent a long time in London in the past, in addition, I
wanted to do an end to end project involving data scraping.

## Data collection

In this project I collected data for around 20,000 properties (after data clearning)
via scraping the UK property website right-move.

This included scraping key information such as the price, address, 
number of bedrooms and bathrooms, closest distance of train stations and the property 
type. In a addition I scraped the property plan images as these often contain text with
the area of the property. An example of this is shown below.

![alt-text-1](/images/propertyplan1.png)

## Data cleaning and feature engineering

In addition, to cleaning up any text with python string functions and regular expressions, a major 
part of the data cleaning involved extracting text from the property plans. This made use of 
openCV thresholding and pytesseract. I also converted all addresses to gpu coordinates using the google maps
api in python. This allowed me to engineer a key feature, the distance to central address in London, Picadilly
Circus. 

## Data visualization 

![alt-text-1](/images/AllPlots.png)

![alt-text-1](/images/london.png)
## Model building

## Final result
