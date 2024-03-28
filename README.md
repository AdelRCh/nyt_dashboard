# New York Times: A Dashboard

This repository is inspired by a capstone group project undertaken during the @DataScientest data engineering boot camp alongside [KSuljic](https://github.com/KSuljic/) and [Jeahy.](https://github.com/Jeahy)

The initial group repository can be found [here.](https://github.com/KSuljic/ny_project) As such, you may consider this repository as a fork of sorts.

## What changed?

* **newswire_acquisition:** The Newswire acquisition script works as a shell command, and users can provide parameters to update the database.
* **dash_app:** The GUI is multipage, allowing for easier code management.
* **ny_import:** Few modifications made, mainly to the way data is stored, so that I may use this feature alongside the NY Times Archive API.
* **archive_acquisition (new):** The script allows us to acquire archive data, beefing up the dataset significantly. Said dataset shares the same format (and will share the same database) as ny_import.
* **books_acquisition (new):** Not implemented yet, but the intent is to monitor nonfiction book charts weekly.
* **mongodb:** merely provides a MongoDB image and its configuration.
* **api (new):** not implemented yet, but it will take on the bulk of the data calls that the dash_app currently performs. The goal in this repo is to implement OAuth.

For this project to work locally, please acquire an API code from [the New York Times' developer portal](https://developer.nytimes.com/) and load it as an environment variable as follows:

~~~
export "**NYTIMES_API_KEY**=<your_api_key>"
~~~

Furthermore, as **this project uses a MongoDB database,** please ensure that a database instance (preferably the one provided here) is running.

Contained within both folders are Dockerfiles for those looking to create containers for testing. Requirement files are also provided for each folder.

That said, please provide a .env file with the following:

* **newswire_acquisition**'s container is missing a critical environment variable: the NY Times API key (**NYTIMES_API_KEY**). One can also supply their own **MONGODB_ADDRESS** and **MONGODB_PORT** to customize those values within the container.
* **dash_app** can also take MONGODB_ADDRESS and MONGODB_PORT as custom arguments, as needed. In the future, these values will go to the API instead.

## Upcoming changes

I will expand this repository to include a revamped portal where I will use the NY Times' various APIs. Expect gradual changes to occur over time as I build/remake/tweak sections one by one to account for higher data volume.

Also, and this might be unnecessary, a healthy dose of Cython and a few bulkWrites (MongoDB) might barge in to speed up runtimes.
