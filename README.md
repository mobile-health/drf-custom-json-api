# drf-custom-json-api

This library is extended from https://github.com/django-json-api/django-rest-framework-json-api 

* Documentation: http://django-rest-framework-json-api.readthedocs.org/
* Live demo (resets every hour): http://json-api.jerel.co/
* Format specification: http://jsonapi.org/format/

We customize the response of pagination 
 from:
 ```
    {
        "links": {
            "prev": "http://example.com/api/1.0/identities",
            "self": "http://example.com/api/1.0/identities?page=2",
            "next": "http://example.com/api/1.0/identities?page=3",
        },
        "data": [{
            "type": "identities",
            "id": 3,
            "attributes": {
                "username": "john",
                "full-name": "John Coltrane"
            }
        }],
        "meta": {
            "pagination": {
              "count": 20
            }
        }
    }
 ```
 to:
 ```   
    {
        "data": [{
            "type": "identities",
            "id": 3,
            "attributes": {
                "username": "john",
                "full-name": "John Coltrane"
            }
        }],
        "meta": {
            "pagination": {
              "count": 20
            },
            "links": {
                "prev": "http://example.com/api/1.0/identities",
                "self": "http://example.com/api/1.0/identities?page=2",
                "next": "http://example.com/api/1.0/identities?page=3",
            },
        }
    }
 ```   