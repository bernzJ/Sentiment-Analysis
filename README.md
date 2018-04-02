# Sentiment-Analysis
Analytic tool allowing to analyze reddit new posts/comments feed searching for specific keywords/sentences to be then sent to score apis like mashape.

# Usage 
Requires minimum python 3.0~, run setup.py to install packages dependencies. Put api(s) in `api.json` and comments in `keyword.json`. 
*Example config: (note: remove comments)*
```javasript
[
    {
        // [Required] The api url.
        "url": "api_url",
        // [Required] The api name.
        "name": "api_name",
        // [Required] Method used: POST, GET, PUT etc..
        "method": "POST",
        // [Optional] If any additional headers needed, keys for api may need this.
        "headers": {
            "my_secret_key": "keyboardcat",
            "accept": "*"
        },
        /** [Required] data sent via POST/GET etc. in the body of the request. The only modifiable value here is: `_the_api_field_name`.
        *   `data_string` is the text sent to be scored from the api, field may change for each apis.
        *   More values may be added if required. 
        */
        "json_data": {
            "_the_api_field_name": "data_string",
            ...
        }
    }
]
```
