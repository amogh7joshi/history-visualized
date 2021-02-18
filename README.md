# History Visualized

![U.S. President Timeline Example Image](presidents/images/us-president-life-and-terms.png)

Visualizations of historical data in the fields of history, anthropology, theology, and geography.

## Research

Each directory within this repository is home to a specific research submodule, within which
data is acquired, parsed, and developed into a diagram.

Currently, research is (and has been) conducted in the following modules:

### [United States Presidents](https://github.com/amogh7joshi/history-visualized/tree/master/presidents)

![U.S. President Executive Orders](presidents/images/us-president-executive-orders.png)

Research and visualizations of different aspects of the presidential terms and to an extent, the actual lives
of past Presidents of the United States.

### [Nations of the World](https://github.com/amogh7joshi/history-visualized/tree/master/nations)

Research and visualizations of historical and geographic data surrounding the current nations of the world.

### [World Macroeconomics](https://github.com/amogh7joshi/history-visualized/tree/master/money)

Research and visualizations of historical macroeconomic data, such as nation GDP and GWP, as well as share of 
the world market by each country over time. 

## Visualizations

In order to generate the visualizations, data is first gathered from a source (see [sources](https://github.com/amogh7joshi/history-visualized#sources)). 

If data is gathered from a verified external source, then it is parsed using a specific method created specifically for that piece of data. Generally, however, 
data is scraped and parsed directly from Wikipedia using the [Python](https://github.com/goldsmith/Wikipedia) Wikipedia API. In this case, each individual module 
constructs different "processing functions", which have their own specific functions to parse through pre-processed HTML data returned from a specific Wikipedia page.

The pre-processing is done by the different methods in the `query` module, which contains a number of methods which automatically parse a specific search term, 
find the Wikipedia page corresponding to the term, and return the pre-parsed page data (e.g. removing excess tags and cleaning up the text).

Since this process generally takes a bit of time initially, and this time only increases with the number of individual API requests you need to send for each of the 
different pages on Wikipedia, the `query` module also contains an information storing lazy loader, which after processing the data once, saves it to a binary storage file
and on each subsequent usage loads data straight from the binary file rather than sending more requests.

From there, the data is transformed into the visualizations you see using different functionalities of [matplotlib](https://github.com/matplotlib/matplotlib).

## Sources

Data is either scraped and parsed directly from Wikipedia (see [visualizations](https://github.com/amogh7joshi/history-visualized#visualizations) for in-depth information on this process), 
or through verified external sources (e.g., the Maddison Project for historical 
world and nation GDP data). The visualizations are generated in the individual research submodules using matplotlib and numpy from this data, 
and may not be used without permission.

## License and Usage

All the code in this repository, including the top-level `query` and `graphics` modules as well as the individual research submodule files, are
licensed under the Apache-2.0 License. You are free to download the code and try out the visualization generation for yourself (it's 
actually quite an intuitive process once you understand it!). 

Any of the generated visualizations can be used (non-commercially), but the watermark must be retained and this repository cited with it.



