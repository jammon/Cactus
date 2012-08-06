## What is Cactus

Cactus is a simple but powerful [static website generator](http://mickgardner.com/2011/04/27/An-Introduction-To-Static-Site-Generators.html) using the [Django template system](http://docs.djangoproject.com/en/dev/topics/templates/). Cactus also makes it easy to develop locally and deploy your site to S3 directly. It works great for company, portfolio, personal, support websites and blogs.

To get a quick overview [watch this short video tutorial](https://vimeo.com/46999791).

Cactus is based on the idea that most dynamicness on websites these days can be done using Javascript while the actual site can stay static. Static websites are easy to host and typically very fast.

I developed Cactus because I wanted a standard, easy system that designers at [Sofa](http://www.madebysofa.com) could use to build and deploy fast websites. So typical users would be designers that are tech-savvy, want to use templates, but don't like to mess with setting up django or S3.

Since then it has evolved quite a bit with a plugin system that supports blogging, spriting, versioning and is extensible.

You can find more discussion about static site generators in this [Hacker News discussion](http://news.ycombinator.com/item?id=2233620).

### Examples

- http://www.madebysofa.com -  Sofa website
- http://docs.enstore.com - Enstore documentation website

There is also an example blog project included.

## Super quick tutorial for the impatient

Install Cactus with the following one liner

	sudo easy_install https://github.com/koenbok/Cactus/zipball/master

If you saw no errors, you can now generate a new project
	
	cactus create ~/www.mysite.com

To start editing and previewing your site type the following. Cactus will start a small webserver that rebuilds your site as soon as you edit a file. You can stop the server with control-c.
	
	cd ~/www.mysite.com
	cactus serve

Once you are ready to deploy your site to S3 you can run the following. You will need your [Amazon access keys](https://payments.amazon.com/sdui/sdui/helpTab/Checkout-by-Amazon/Advanced-Integration-Help/Using-Your-Access-Key). If you don't have one yet, [read how to get one here](http://www.hongkiat.com/blog/amazon-s3-the-beginners-guide/).

	cactus deploy

Voila. Your website generated by Cactus and hosted on S3!

## Extended guide

### Creating a new project

You can create a new project by generating a new project structure like this. Make sure the destination folder does not exist yet.

	cactus [path] create

If you did not see any errors, the path you pointed to should now look like this.
	
	- build					Generated site (upload this to your host)
	- pages					Your actual site pages
		- index.html
		- sitemap.xml
		- robots.txt
		- error.html		A default 404 page
	- templates				Holds your django templates
		- base.html
	- static				Directory with static assets
		- images
		- css
		- js
	- plugins				A list of plugins. To enable remove disabled from the name

### Making your site

After generating your site you can start building by adding pages to contents, which can rely on templates. So for example if you want a page `/articles/2010/my-article.html` you would create the file with directories in your pages folder. Then you can edit the file and use django's template features.

### Building your site

When you build your site it will generate a static version in the build folder that you can upload to any host. Basically it will render each page from your pages folder, copy it over to the build folder and add all the static assets to it so it becomes a self contained website. You can build your site like this:
	
	cd [your-cactus-path]
	cactus build

Your rendered website can now be found in the [path]/build folder. Cactus can also run a small webserver to preview your site and update it when you make any changes. This is really handy when developing. You can run it like this:

	cactus serve

### Linking and contexts

Cactus makes it easy to relatively link to pages and static assets inside your project by using the standard context variables STATIC\_URL and ROOT\_URL. For example if you are at page `/blog/2011/Jan/my-article.html` and would like to link to `/contact.html` you would write the following: 

	<a href={{ ROOT_URL }}/contact.html>Contact</a>


### Deploying
	
Cactus can deploy your website directly to S3, all you need are your Amazon credentials and a bucket name. Cactus remembers these in a configuration file name config.json to make future deploys painless. The secret key is stored securely in the Keychain or similar services on other OSs.
	
	cactus deploy

After deploying you can visit the website directly. You can find a deploy log at [site url]/versions.txt.

### Extras

Cactus will auto generate a robots.txt and sitemap.xml file for you based on your pages. This will help bots to index your pages for Google and Bing for example.
