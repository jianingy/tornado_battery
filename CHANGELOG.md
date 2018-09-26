# 2019-09-26

- schema now supports schema(reply=True), which allows user to return a customized dict object.
- schema now supports schema(error=ERROR) to handle exceptions.
  - if ERROR == True, a default handler will be used;
  - if ERROR is callable, it will be called with (handler, exception) as arguments
  - otherwise, the exception will be raised
- a brand new entry point been added. Please refer to example greetings
