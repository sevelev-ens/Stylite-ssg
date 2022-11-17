**Stylite** is a naive, straightforward and fast static site generator in Python for sites with **strong centralized hierarchy** stored as **tabular file** `.csv`.


## Launch the webserver :

```python server.py```

## Generate the website into the folder `_site`

```python server.py build```


Mention all the pages in the file `central.csv`. Any variable `variable_name` can be created as separate column. It could then be referred to as `{{page.variable_name}}` in the template file in `_layouts` folder (uses Jinja template).

The static files are reported in the file `static.csv` are copied to the folder _site during the generation, with no further transformation.
