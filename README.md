# Auto Upload Files to Telegraph as Notes

### What is it？

It's a script helps you upload batches of images to telegraph at once, supporting jpg,png,gif. This way you don't need to upload them one by one manually.

For the pics over 5MB which is the max size for telegraph, it can also automaticlly generate a compressed copy of the original image and upload it.

Isn't that cool, ha?

### How does it works?

The script basically using telegraph.api to create the artical. 

First it scans the folder and upload the pics to telegraph one by one, then collect the pic online link and make it a <img> tag, then add it to the html code.

Finally, pubilsh the artical.

### How to use？

This is a script written by python. 

To use it, you have to install python3 and required packages.

> Use with Terminal

1. Install Dependencies

```
pip install -r requirements.txt
```

2. Modify the token of the 214th line of file "telegraph--pic-uploader_v1.1.py" to your Telegraph Token

```
    token = "your token"
```

3. Run

```
python .\telegraph--pic-uploader_v1.1.py -d  [directory]
python .\telegraph--pic-uploader_v1.1.py -b  [Parent directory of multiple directories]
```

