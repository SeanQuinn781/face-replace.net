Running the app in prod

Client:

to build the client run:

``` npm run build ``` 


to run the client run:
``` pm2 -u jo serve build 3000 --spa ```

see the nginx config to enable a proxy to port 3000


Backend:


