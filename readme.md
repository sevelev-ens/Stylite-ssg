![](/static/Stylite.svg)

# Stylite

**Stylite** is a naive, straightforward and fast static site generator in Python for sites with strong **centralized hierarchy** stored as **tabular file** `.csv`.

## To add: Showcases

### Launch the webserver :

```python server.py```

### Generate the website into the folder `_site`

```python server.py build```

## Content organization

Mention all the pages in the file `central.csv`. Any variable `variable_name` can be created as separate column. It could then be referred to as `{{page.variable_name}}` in the template file in `_layouts` folder (uses [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) templating to which Jekyll and Liquid are similar).

The static files are reported in the file `static.csv` and will be copied to the folder `_site` during the generation with no further transformation.

The engine won't crawl all the folders searching for the content, you should explicitely register the pages in the file `central.csv` and deposit the text content anywhere. The server will convert `md` source to `html` and apply the template stated in the central file.  All page variables usually put into `yaml` frontmatter live in `central.csv` as well.

## Engine

The site is built, served by a Python http server in `server.py`, prone to infinite customization and tweaking.

*Stylite* < Ecclesiastical Greek *στυλίτης* `stulítēs` < Ancient Greek *στῦλος* `stûlos` ‘[column](https://pandas.pydata.org/), pillar’. Column is a minimal ordered data structure.
