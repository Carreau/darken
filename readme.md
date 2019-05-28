# apply black only on modifed lines.

POC, still a lot of work. 

## what

```
darken --since <git commitish>
```

Will (try to) reformat only modified lines since `<commit-ish>`

or 
```
darken --range 12-34,64-67 foo.py
```

Should only reformat line 12-34 and 64-67 of foo.py.

# how

Looking at black internal it seem relatively hard to pass a flag tell it to only
refactor some nodes. But, black support fmt:on/off comments; 

So this : 

 - insert comments; 
 - apply black
 - remove the comments it added. 
 - TADA (TM)

Long term API design: 

Get - some – integration with git; 
I'm thinking something along: 

```
$ darken --since <commitish>
```

It would run git in the BG, figure out which files and which lines have changed
and apply to black to relevant lines. 

I'm thinking that if the changed lines represent a significant portion of the
file we could expand what need to be reformatted. Th metric for this need to be
determined. I prefer the `$ darken --since` to a `$ darken <a given commit
only>` as it will correctly handle many things like merges, multipple-commits
branches...etc.

## Issues: 

This is an issue: 

https://github.com/python/black/issues/560


