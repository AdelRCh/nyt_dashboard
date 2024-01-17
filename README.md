# NY Newswire API implementation

This repository contains my contributions to a group project within the DataScientest boot camp, sorted as follows:

* **newswire_acquisition:** data acquisition from the NY Times' Newswire API endpoints and storage into MongoDB
* **dash_app:** a GUI made using Dash, with some MongoDB aggregation requests contained for some of the callbacks demonstrated. Note that the GUI is incomplete in this repository.

For this project to work locally, please acquire an API code from [the New York Times' developer portal](https://developer.nytimes.com/) and load it as an environment variable as follows:

~~~
export "NYTIMES_API_KEY=<your_api_key>"
~~~

Furthermore, as **this project uses a MongoDB database,** please ensure that a database instance is running.

Contained within both folders are Dockerfiles for those looking to create containers for testing. Requirement files are also provided for each folder:

* **newswire_acquisition**'s container is missing a critical environment variable: the NY Times API key. One can also supply their own MONGODB_ADDRESS and MONGODB_PORT to customize those values within the container.
* **dash_app** can also take MONGODB_ADDRESS and MONGODB_PORT as custom arguments, as needed.



