

#**E.M.T.E** 
__*(Exchange Matching and Trading Engine)*__
- - -

##**Requirement**
 - Install [web2py](http://www.web2py.com/).
 - Install [tornado web server ](http://www.tornadoweb.org/en/stable/). (Tornado v4.3)
 -  Web browsers.

---

##**How to run EMTE-TRADING application.**

**1.** *Start web2py. (For more information, visit [web2py overview](http://web2py.com/books/default/chapter/29/03/overview) )*

**2.** *Navigate to application module, and run matching.py.*
  Matching.py takes 2 arguments:
  * **-p**:  port number it listen to. Each ticker has different port number.
  *  **-t**: a ticket symbol. 
	
  Users should insert valid value to the product table before calling **matching.py**.
  The example below assumed that all tickers symbol is already stored in the database. 
 
  ```
  cd applications/emte_trading/modules/
  ```
		
  Each ticker is associated with different port number. 
		
  ```
  python matchingserver.py -p 8888 intc
  ```
  ```
  python matchingserver.py -p 8880 gs
  ```

**3.** *Start  log2db deamon (one per product)*

  Rationale, decouples the job of logging to db from the job of logging to file.
  

  ```
  python web2py.py -S trading  -M -R applications/trading/modules/log2db.py -A intc
  ```
- - -

##  **Overview**
  > EMTE is a Exchange Matching Engine (think of NYSE and Nasdaq) and a Trading Platform that connects to it. It is built in Python with web2py and Tornado. It uses comet via html5 websockets for asynchronous information delivery. The web interface uses jQuery and processing.js for drawing.
  
**1. The Exchange Matching Engine** 
 
 As the name implied, EMTE function can be divided into two major roles, the exchange  matching engine, and the trading platform. In order to start the exchange matching engine, users run web2py EMTE application, open the application in your favorite web browser.
 
 * **First time users**:
     
 When you run the application for the first time, don't run **matching.py** just yet. Make sure that you follow these steps:

   *  Signup. There are 2 modes for users when they sign up: *manager*, and *clients/traders*. As a *manager*, you have permission to create/register any product to trade. While the *clients/traders* only trade products created by the *manager*.

    ![RegisterUser](http://i.imgur.com/77eeBeh.png?1)


   * Register product (log in as manager). Make sure that you match each port of registered ticker with the port when run **matching.py** here. Note that each port is assigned with diferent port number. **Matching.py** uses websocket protocol to handle request from client. Therefore, you need to specify **web socket protocol** in **Ws Url** form.

     Simply click on  *Products* tab. The form to insert product is shown as below: 

     ![RegisterAapl](http://i.imgur.com/rxRBrUH.png?1)      ![RegisterGs](http://i.imgur.com/vNjesGH.png?1)


 * **Trading matching engine web interface.** 
 
 Before open the web interface  to trade, remember to run **matching.py**. The web interface communicates with **matching.py** base on Tornado web socket. It acts as another server communicate with clients. Therefore, the matching engine must start to listen to clients.

 ![Imgur](http://i.imgur.com/djIePYN.png?1)

 When entering the *Products* page, this is the response from matching engine. 

 ![Imgur](http://i.imgur.com/QZptWt6.png?1)

 **EMTE** allows users to trade when there is record of product in the database.  
 User can submit order by check in the order options box, then click on the screen. When you hover the mouse on the page, there is a crosshair that show you the quantity at specific price.

 The horizontal axis tracks the price of our finacial product. Price increases as the crosshair hovering to the right, and decreases as the crosshair hovering to the left. Similarly, if users move the crosshair up, the quantity increase, and decrease otherwise.

 Users can submit order by clicking on the screen, or by a trading program. 
  
  ![EMTE interface](http://i.imgur.com/3PBoBuF.png?1)


**2. The Trading Platform** 

 As mention above, users can mannually clicking on the screen at the price they are willing to pay. One advance feature of **EMTE** is that it allows *algorithmic, and automated trading*.  
 Users choose to ultilize such feature can implement their trading algo and communicate with the matching engine. The example below is the random trade of Apple Inc. stock from robot trader. Note that *port 8888* is currently associated with *appl* ticker in our database.  
 Traders can track their account balance any time, simply by clicking to the **P&L**. This open a page that updates balance account in real time. 

 ![Imgur](http://i.imgur.com/uOzKZvF.png?1)

 [For more information](https://vimeo.com/18282084)


- - - 


