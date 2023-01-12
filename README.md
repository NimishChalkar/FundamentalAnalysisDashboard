# Fundamental Analysis Dashboard

Here we are automating a method called fundamental analysis to pick the best stocks to invest in any given sector. Essentially, a screener which will pick the top stocks for us based on the underlying grading algorithm.
    
## Overview of Data

Data shows the fundamentals of various businesses in different sectors which help us in determining the corporate value and give us the top shares in which common investors can look into.  

<img width="621" alt="image" src="https://user-images.githubusercontent.com/59665584/212155588-3b41411d-1b3a-4e88-9f62-7302bba7d348.png">


***Data Source:*** 

  1. https://eodhistoricaldata.com/ (You need a paid subscription for using the API)
    
<img width="486" alt="image" src="https://user-images.githubusercontent.com/59665584/212160495-bd35740d-9df2-4789-8363-1a4fa696466c.png">

    
  2. Yahoo Finance (*for ticker prices*) 

## Preprocessing

  •Data cleaning using pandas and numpy libraries  
  •Removing null values  
  •Converting marketCap to billions   
  •Grouping according to the marketCap (Small, Medium, Large)  

## Grading

The grading algorithm is based on distribution analysis of values for a certain metric for a specific sector

![image](https://user-images.githubusercontent.com/59665584/212153870-9e05031e-38da-4738-b0f5-ddc62ae57fb9.png)

For instance, to evaluate a stock's net margin, I would look at the net margins of all the stocks in the Communications sector and assign a percentile to the stock's net margin depending on where it falls in the distribution of values.

<img width="353" alt="image" src="https://user-images.githubusercontent.com/59665584/212157996-8a1b31a6-1f35-4b23-b7e6-d9c99c5e2189.png">

For metrics where a lower value is considered better, such as P/E ratios, the algorithm will use the 10th percentile as the basis for grading. So if a stock in the Industrials sector has a P/E ratio of 10 and that is in the 10th percentile of all P/E ratios for Industrials stocks, it will be rated A+.

To determine a stock's overall rating, the grades are then changed into numbers for each category, combined together, and multiplied.

## PowerBI Dashboard

![image](https://user-images.githubusercontent.com/59665584/212151629-fbe118da-b857-4983-afb9-936f542e5155.png)

***Small Cap***

![image](https://user-images.githubusercontent.com/59665584/212151877-86c52813-ea9f-4913-bd96-961d7fb34e04.png)

***Mid Cap***

![image](https://user-images.githubusercontent.com/59665584/212152049-609d5de1-cb6d-46ad-a43f-151b94a1892b.png)

***Large Cap***

![image](https://user-images.githubusercontent.com/59665584/212152162-dfc9c001-54be-4f91-bfdf-79629c86008e.png)



***Note***

•All the data required for the project is publicly available  
•Fundamental analysis provides us the indicators to gauge our understanding on how suitable a company is for us to invest in  
•The indicators by nature do not guarantee the returns. They, only help us in making better decisions  
•From the perspective of an equity investor, the goal of fundamental analysis is to pick stocks with the right valuation and that have the potential for growth   
•On the other hand, technical analysis with price charts can be used to find a profitable stock trade signal  
