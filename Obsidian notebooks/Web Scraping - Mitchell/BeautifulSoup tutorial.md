# BeautifulSoup tutorial
Created: 2021-12-16 21:26
Tags: #beautiful-soup #html #web-scraping #python 
***

## Parser
- `lxml` = fast, external C dependency
- `html.parser` = internal
- `html5lib` = slow, external Python dependency

## Opening links
open filehandle
```python
with open("index.html") as fp:
    soup = BeautifulSoup(fp, 'html.parser')
```

string to link
```python
soup = BeautifulSoup("<html>a web page</html>", 'html.parser')
```

string of html
```python
soup = BeautifulSoup('<b class="boldest">Extremely bold</b>', 'html.parser')
```

## HTML object types 
HTML defaults
```python
from bs4.builder import builder_registry
builder_registry.lookup('html').DEFAULT_CDATA_LIST_ATTRIBUTES

{'*': ['class', 'accesskey', 'dropzone'], 'a': ['rel', 'rev'], 
'link': ['rel', 'rev'], 'td': ['headers'], 'th': ['headers'], 
'form': ['accept-charset'], 'object': ['archive'], 'area': ['rel'], 
'icon': ['sizes'], 'iframe': ['sandbox'], 'output': ['for']}
```

### Tags and attributes
- access attribute value of tag via `soup.tag[attr]`
	- where `soup::BeautifulSoup`, `tag` is a tag and `attr` is an attribute of `tag`
- every tag has a **name**
	-  `tag.name`, change via `tag.name = [new name]`
- tags can have any number of **attributes**
	- e.g. `<b id="boldest">` has an attribute “id” whose value is “boldest”
	- treat the tag as a dictionary: `tag[id]`
	- dictionary of attributes `tag.attrs`

### Modifying tag attributes
- use dictionary syntax to add/change tag attributes
- change atributes `tag[attr] = ...`
- `del tag[attr]` to remove attribute
- `tag.append()`, `tag.insert(index, ...)`, and `tag.extend()` add attributes

### Multi valued attribtes
- **multi valued attributes **
	- `class` (that is, a tag can have more than one CSS class). 
	- Others include `rel`, `rev`, `accept-charset`, `headers`, and `accesskey`
	- given multi-valued attribute `multi_attr`, the corresponding values are stored as `Dict[str, List[str]]`
		- e.g. `tag[multi_attr] = [val1, val2, ...]`
	- no multi valued attrs in XML
- tag.attr.`get_attribute_list(...)` -> always returns a list

multi-valued attributes
```python
css_soup = BeautifulSoup('<p class="body strikeout"></p>', 'html.parser')
css_soup.p['class']
# ['body', 'strikeout']
```

multi_valued_attributes=None
```python
no_list_soup = BeautifulSoup('<p class="body strikeout"></p>', 'html.parser', multi_valued_attributes=None)
no_list_soup.p['class']
# 'body strikeout'
```

No multi valued attrs in XML by default -> need to pass `multi_valued_attributes`
```python
class_is_multi= { '*' : 'class'}
xml_soup = BeautifulSoup('<p class="body strikeout"></p>', 'xml', multi_valued_attributes=class_is_multi)
xml_soup.p['class']
# ['body', 'strikeout']
```

### NavigableString
A string corresponds to a bit of text within a tag. Beautiful Soup uses the `NavigableString` class to contain these bits of text:
```python
soup = BeautifulSoup('<b class="boldest">Extremely bold</b>', 'html.parser')
tag = soup.b
tag.string
# 'Extremely bold'
type(tag.string)
# <class 'bs4.element.NavigableString'>
```

Features
- Convert to unicode: `str(NavigableString)`
- cannot be edited inplace but can be replaced: `tag.string.replace_with("new string")`

**comments** are a type of NavigableString
```python
markup = "<b><!--Hey, buddy. Want to buy a used parser?--></b>"
soup = BeautifulSoup(markup, 'html.parser')
comment = soup.b.string
type(comment)
# <class 'bs4.element.Comment'>
```

### BeautifulSoup objects
- represents entirety of parsed document
- similar to `Tag` object, e.g. `soup.tag`
- doucment name: `soup.name`

Combine two parsed documents
```python
doc = BeautifulSoup("<document><content/>INSERT FOOTER HERE</document", "xml")
footer = BeautifulSoup("<footer>Here's the footer</footer>", "xml")
doc.find(text="INSERT FOOTER HERE").replace_with(footer)
```

## Navigating the tree
- `tag.attr` gives you first matching tag, use `soup.find_all(tag)` to get all instances of the tag
- `tag.contents` = children of a tag -> `List[str`
	- iterator: `for child in tag.children:`
- child vs descendants, e.g.`<head><title>Story</title></head>`
	- `title` is a child of `head`
	- `title` has child 'Story' 
	- both 'Story' and `title` are descendants of `head`
- strings are considered children
	- if the only child is a `NavigableString`, then the child is accessed as `tag.string`
	- if a tag has only one child, and that child has a `.string`, then the first tag has `.string`
	- e.g. 'Story' = `title.string`, but also `head.string` = 'Story'
	- else, `.string = None`
- iterator for strings over any tag: `tag.strings` or `tag.stripped_strings` (no whitespace)
- going up the tree: `.parent` for direct parent and `.parents` to iterate over all parents

### Siblings
```python
sibling_soup = BeautifulSoup("<a><b>text1</b><c>text2</c></b></a>", 'html.parser')
print(sibling_soup.prettify())
#   <a>
#    <b>
#     text1
#    </b>
#    <c>
#     text2
#    </c>
#   </a>
```
The `<b>` tag and the `<c>` tag are at the same level: they’re both **direct children of the same tag.** We call them siblings. When a document is pretty-printed, siblings show up at the **same indentation** level.
- `.next_sibling` moves from b -> c, and `previous_sibling` vice versa
	- however, `previous_sibling` won't work on b because nothing above b 
- iterators: `next_siblings` and `previous_siblings`

```python
for sibling in soup.find(id="link3").previous_siblings:
    print(repr(sibling))
```

### Reconstructing how the document was initially parsed
- `.next_element` = what was parsed immediately after the current tag/string; opposite = `.previous_element`
- iterators: `next_elements` and `previous_elements`

## Searching the tree
### Basic overview
- look down the tree: `find_all` and `find`
- up the tree: `find_parents` and `find_parent`
- siblings: `find_next_sibling(s)` and `find_previous_sibling(s)`
- parsed elements: `find_all_next`/`find_next` and `find_all_previous`/`find_previous`

### CSS selectors
https://facelessuser.github.io/soupsieve/

### `Name` argument to `find_all`
> the value to name can be a string, a regular expression, a list, a function, or the value True.
1. string = html tag [[HTML tags]]
2. regex = similar to a function, finds all tags that match the regex
3. list of tags
4. anything that doesn't match a tag will be used to look at tag attributes

`True` = find all tags, but none of the text strings
```python
for tag in soup.find_all(True):
    print(tag.name)
# html
# head
# title
# body
# p
# b
# p
```

function: `True` for a match, `False` otherwise
- if input is a specific attribute like `href`, then function input will be attribute value, not the full tag
- e.g. `True` if a tag defines the “class” attribute but doesn’t define the “id” attribute:
```python
def has_class_but_no_id(tag):
    return tag.has_attr('class') and not tag.has_attr('id')
	
soup.find_all(has_class_but_no_id)
# [<p class="title"><b>The Dormouse's story</b></p>,
#  <p class="story">Once upon a time there were…bottom of a well.</p>,
#  <p class="story">...</p>]
```

### Keywords arguments to `find_all`
- kwarg use 
	- specify values for certain attributes, and return tags matching these conditions
	- standalone or in conjunction with `name` or with other kwargs
- Common keyword tags 
	- HTML: `id`, `href`
	- CSS classes: `class_`
		- a tag can have multiple values for `class` attribute, so `find_all` returns any match
	- Strings: `string=...`, e.g. string, regex, list, function, `True`
- find all tags with matching values, regardless of tag
- set `=True` to find all values for tag
- most attributes can be filtered using kwarg syntax, 
	- except `name`, which is an argument name in function definition
- any argument, including `name` can be filtered by setting the `attrs: Dict[str, str]`
	- e.g. `attrs={'name' : ['email', 'whatever']}`

### Selecting CSS
See [[#CSS selectors]]
- `class_` works for finding tags that contain a given CSS class, but each tag may have more than one
- `class_` only supports exact matches, i.e. order matters

**Find multiple CSS classes**
```python
css_soup.select("p.strikeout.body")
# [<p class="body strikeout"></p>]
```



## References
1. [Beautiful Soup Documentation — Beautiful Soup 4.9.0 documentation (crummy.com)](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#the-name-argument)