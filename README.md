Focus to create a web application that allows users to chart their asset performance over time
-> Login feature
    -> Email, First Name, Last Name, Password
-> Homepage where you enter your information, a form that allows you to
    -> Type of asset, date purchased, amount spent, number of shares purchased, etc. 
    -> Submit as a CSV or submit as a form?
-> Homepage that shows owning of assets, pie chart of asset holdings
-> Assets can be grouped by class, crypto, stocks, real estate, etc.
-> Export data of your holdings as a CSV file 
-> Find a way to connect this to a centralized exchange API like coinbasepro. s



PORTFOLIO TRACKER LOGIC
-> Say we bought X on 0/1/12
    -> Chart the price movement using price x quantity for each date
-> Now we bought Y on 0/1/13
    -> Now there is a new segment in the graph, price movement is calculated by y * its price per date + x + its price per date 
-> Three variables
    ->New price movement is old + 