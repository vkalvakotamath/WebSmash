I haven't tried out the websmsh.py because the use case here is that of a dating website. The configuration would be more or less the same, but the changes to be made would depend on the HTML containers and stuff. What you could do is first try out the browser dev tools on the wbesite nad see which containers have profile bio, pictures, etc. and modify the code and then run it. 

If you already have scraped pictures and bio into the hierarchy of:
- WebSmash
    - Profiles
        - Profile-1
          - Picture-1.png/jpg/jfif
  
          - Profile-1.txt
         
         - Profile-2
          - Picture-2.png/jpg/jfif
           
           - Profile-2.txt
  
    - Templates
        - index.html
        - win.html
    
    - app.py
    
    - ratings.json
    
    - websmash.py
    

with whatever you want to compare, put it in the \Profiles directory and run app.py and open the localhost page to get started.
