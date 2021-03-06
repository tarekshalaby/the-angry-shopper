Scraping Cairo's supermarkets to compare prices and track changes.

![The Angry Shopper logo](https://theangryshopper.com/static/images/the-angry-shopper-logo.png)

## :zap: Live at [theangryshopper.com](https://theangryshopper.com)
The Angry Shopper is a free and open-source platform that tracks prices of all products available across different supermarkets. In one place, you can easily compare prices of all prducts and see what's cheaper where. Moreover, it lets you browse each supermarket individually, highlighting the change in prices over time. So it's easy to see how much each product has gone up and down in price, and when. 

> In addition to saving us money, The Angry Shopper also exposes how supermarkets play around with their prices to trick us into paying them more for less. 

## :gear: How it works
Every day, The Angry Shopper crawls the websites of the supermarkets on the platform, and checks for the prices of every product they sell. All the data is then saved in a database that logs the changes, and displays that information for us. Once the same products across the different supermarkets have been linked together in the database, they appear in the "Compare" section of the platform where you can see the prices for the same products side-by-side across the different supermarkets.

## :two_hearts: Contributing to The Angry Shopper
This is a free and open-source project that's aimed to be for us, and by us. We all grocery-shop and it's time we didn't get ripped off for it. There are many ways in which you can contribute to the project, including:

:speech_balloon: Ask for new features by submitting an issue

:warning: Report any bugs you come across and help us fix them

:pencil: Manage all of the bugs and features the growing team needs to work on

:open_file_folder: Connect the same products across the different supermarkets so that The Angry Shopper can compare their prices

:tv: Marketing effort to grow reach

:woman_technologist: If you know Python, you can clone the repo and push your code

:man_artist: If you're a designer, let's enhance the UI

:woman_mechanic: If you're into servers and DevOps, check out the setup below and help us make this scalable


## :computer: Technical details
I'm not a developer, but I got hit by COVID and while self-isolating, learned to program in Python and built the entire platform from scratch. I watched endless hours on YouTube, with most credit going to the phenomenal [Corey Schafer](https://www.youtube.com/user/schafer5) whose free online videos taught me pretty much everything I know. 
* Built in Python3 using [Flask](https://flask.palletsprojects.com/en/1.1.x/) as the framework, and [SQLAlchemy](https://www.sqlalchemy.org/) as the ORM. I tried my best, but anyone with a bit of experience can surely improve/refactor the code
* Used MySQL as the database, just because I'm used to it from previous data-driven projects. Happy to migrate to Postgres or something else if it's better.
* UI built with [Bulma.io](https://bulma.io/) as the CSS framework, with SASS. Used [Iconify](https://iconify.design/)'s free svg icons. 
* Hosting on a [Linode](https://www.linode.com/) server (starting with the smallest, $5 monthly plan), with Ubuntu, Nginx, Gunicorn, MySQL and a few of the Python/Flask libraries.
* Bought the domain from [Name.com](https://www.name.com/), and used [Let's encrypt](https://letsencrypt.org/) for a free, renewed SSL certificate.

---

### :angry: About me
I'm a techie but what I do doesn't define me. I prefer to be categorized as your typical revolutionary socialist with radical ideas, obnoxious opinions, and an ability to endlessly debate the world and how to change it. I'm a Cairene, a foodie and a wanna-be cook, so The Angry Shopper fits me well, I think.

### :free: License
The Angry Shopper is licensed under Creative Commons Zero v1.0 Universal with the intent of making accessible to anyone, anywhere. 