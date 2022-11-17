# Stylite

**Stylite** is a naive, straightforward and fast static site generator in Python for sites with strong **centralized hierarchy** stored as **tabular file** `.csv`.


### Launch the webserver :

```python server.py```

### Generate the website into the folder `_site`

```python server.py build```

## Content organization

Mention all the pages in the file `central.csv`. Any variable `variable_name` can be created as separate column. It could then be referred to as `{{page.variable_name}}` in the template file in `_layouts` folder (uses Jinja template).

The static files are reported in the file `static.csv` and will be copied to the folder `_site` during the generation with no further transformation.

The engine won't crawl all the folders searching for the content, you should explicitely register the pages in the file `central.csv` and deposit the text content anywhere. All page variables usually put into `yaml` frontmatter should live in `central.csv` as well.

---

*Stylite* < Ecclesiastical Greek `στυλίτης` (`stulítēs`) < from Ancient Greek `στῦλος` (`stûlos`) ‘[column](https://pandas.pydata.org/), pillar’.

